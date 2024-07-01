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
from typing import Any

from api_scoring.scoring import get_score, get_interests
from api_scoring.models import (
    MethodRequest,
    OnlineScoreRequest,
    ClientsInterestsRequest,
)


SALT = "Otus"
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


def check_auth(request: Any) -> bool:
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account + request.login + SALT).encode("utf-8")
        ).hexdigest()
    logging.info(f"{digest}")
    return digest == request.token


def method_handler(request: Any, ctx: Any, store: Any) -> tuple:
    try:
        _method_request = MethodRequest(request.get("body"))
    except ValueError as e:
        _message = str(e)
        logging.error(_message)
        return json.dumps(_message), BAD_REQUEST

    if not check_auth(_method_request):
        logging.info("Invalid authentication.")
        return "", FORBIDDEN

    _arg_dict = request.get("body").get("arguments")

    _online_score_requst, _clients_interests_request = None, None
    try:
        if _arg_dict.get("client_ids", None) is None:
            _online_score_requst = OnlineScoreRequest(_arg_dict)
        else:
            _clients_interests_request = ClientsInterestsRequest(_arg_dict)
    except ValueError as e:
        _message = str(e)
        logging.error(_message)
        return json.dumps(_message), BAD_REQUEST

    if _clients_interests_request:
        _responce_dict = dict()
        for _client in _clients_interests_request.client_ids:  # type: ignore
            _responce_dict[_client] = get_interests()
        ctx["nclients"] = len(_clients_interests_request.client_ids)  # type: ignore
        return _responce_dict, OK

    if _online_score_requst:
        ctx["has"] = _online_score_requst.score
        if _online_score_requst.score == 0:
            logging.error(
                "Invalid arguments. Must be pass phone-email or first_name-last_name or gender-birthday"
            )
            return (
                "Invalid arguments. Must be pass phone-email or first_name-last_name or gender-birthday",
                INVALID_REQUEST,
            )
        if _method_request.is_admin:
            return {"score": 42}, OK
        else:
            return {"score": get_score(_online_score_requst)}, OK
    return "Unknown error", INTERNAL_ERROR


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
            request = json.loads(data_string.decode("utf8"))
        # TODO прописать конкретные исключения
        except Exception as e:
            logging.exception(e)
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
