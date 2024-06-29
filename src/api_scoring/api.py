# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

import datetime
import hashlib

# import abc
import json
import logging
import uuid
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Self, Type

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class RequestORM(type):
    def __new__(
        self: Type[type], name: str, bases: tuple, namespace: dict
    ) -> "RequestORM":
        required_attr: List[str] = []
        non_nullable_attr: List[str] = []

        for k, v in namespace.items():
            if isinstance(v, Field):
                namespace[k] = k
                if v.required:  # type: ignore
                    required_attr.append(k)
                if not v.nullable:  # type: ignore
                    non_nullable_attr.append(k)
        namespace["required_attr"] = required_attr
        namespace["non_nullable_attr"] = non_nullable_attr
        return super().__new__(self, name, bases, namespace)  # type: ignore[misc]


class Field:
    name = ""

    def __init__(self, required: bool = True, nullable: bool = True):
        self.required = required
        self.nullable = nullable

    def __set_name__(self, cls: Self, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Self:
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]


class CharField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if isinstance(value, str):
            instance.__dict__[self.name] = value
        else:
            raise ValueError("CharField must be str")


class ArgumentsField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if isinstance(value, dict):
            instance.__dict__[self.name] = value
        else:
            raise ValueError("ArgumentsField must be dict")


class EmailField(CharField):
    def __set__(self, instance: Self, value: Any) -> None:
        super().__set__(instance, value)
        if "@" not in value:
            raise ValueError(f"{value} isn't valid email")

        instance.__dict__[self.name] = value


class PhoneField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if not isinstance(value, str) or not isinstance(value, int):
            raise ValueError(f"{value} can not be phone number")

        if isinstance(value, int):
            value = str(value)

        if len(value) != 11 or int(value[0]) != 7:
            raise ValueError(f"Invalid phone number: {value}")

        instance.__dict__[self.name] = value


class DateField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        try:
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError as e:
            raise ValueError(e) from e
        instance.__dict__[self.name] = value


class BirthDayField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        try:
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError as e:
            raise ValueError(e) from e
        _current_date = datetime.datetime.combine(
            datetime.date.today(), datetime.datetime.min.time()
        )
        _difference = round((_current_date - value).days / 365.25, 0)
        if _difference > 70.0:
            raise ValueError(f"Invalid birthday: {value}")

        instance.__dict__[self.name] = value


class GenderField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if not isinstance(value, int) or value not in [0, 1, 2]:
            raise ValueError(f"Invalid gender: {value}")
        instance.__dict__[self.name] = value


class ClientIDsField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if not isinstance(value, list):
            raise ValueError(f"Invalid clients ids: {value}")
        instance.__dict__[self.name] = value


class Request(metaclass=RequestORM):
    def __init__(self, _json: Any):
        if _json is not None:
            dict_attr: Dict[str, Any] = json.loads(_json)
        for _attr in self.required_attr:  # type: ignore
            if _attr not in dict_attr.keys():
                raise ValueError(
                    f"Attribute {_attr} must be pass in {self.__class__.__name__}"
                )

        for k, v in dict_attr.items():
            if not v and k in self.non_nullable_attr:  # type: ignore
                raise ValueError(
                    f"Attribute {k} can not be nullable in {self.__class__.__name__}"
                )

        for name, field in dict_attr.items():
            setattr(self, name, field)


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(object):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self) -> bool:
        return self.login == ADMIN_LOGIN


def check_auth(request: Any) -> bool:
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account + request.login + SALT).encode("utf-8")
        ).hexdigest()
    return digest == request.token


def method_handler(request: Any, ctx: Any, store: Any) -> tuple:
    response, code = None, None
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = None

    def get_request_id(self, headers):  # type: ignore
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self) -> None:
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        # TODO прописать конкретные исключения
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            _context = context["request_id"]
            logging.info(f"{self.path}: {data_string!r} {_context}")
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
                except Exception as e:
                    logging.exception(f"Unexpected error: {e}")
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf-8"))
        return


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=8080)
    parser.add_argument("-l", "--log", action="store", default=None)
    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = HTTPServer(("localhost", args.port), MainHTTPHandler)
    logging.info("Starting server at %s" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
