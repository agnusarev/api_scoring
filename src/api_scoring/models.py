import datetime
from typing import Any, Dict, List, Self, Type

ADMIN_LOGIN = "admin"


class RequestORM(type):
    def __new__(
        self: Type[type], name: str, bases: tuple, namespace: dict
    ) -> "RequestORM":
        required_attr: List[str] = []
        non_nullable_attr: List[str] = []

        for k, v in namespace.items():
            if isinstance(v, Field):
                namespace[k] = v
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
        # TODO переписать на регулярку
        if "@" not in value:
            raise ValueError(f"{value} isn't valid email. {value} doesn't have @")

        instance.__dict__[self.name] = value


class PhoneField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if not isinstance(value, str) and not isinstance(value, int):
            raise ValueError(
                f"Invalid type for phone number. {value} is {type(value)}, not str or int"
            )

        if isinstance(value, int):
            value = str(value)

        if len(value) != 11:
            raise ValueError(
                f"Invalid phone number: {value}. Phone must have 11 digits."
            )

        if int(value[0]) != 7:
            raise ValueError(f"Invalid phone number: {value}. Phone must start with 7.")

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
            raise ValueError(
                f"Invalid birthday: {value}. Difference between current date is too long."
            )

        instance.__dict__[self.name] = value


class GenderField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if not isinstance(value, int) or value not in [0, 1, 2]:
            raise ValueError(f"Invalid gender: {value}. Gender must be 0, 1 or 2.")
        instance.__dict__[self.name] = value


class ClientIDsField(Field):
    def __set__(self, instance: Self, value: Any) -> None:
        if not isinstance(value, list):
            raise ValueError(f"Invalid clients ids: {value}. Clients ids must be list.")
        instance.__dict__[self.name] = value


class Request(metaclass=RequestORM):
    def __init__(self, dict_attr: Dict):
        # if _json is not None:
        #     dict_attr: Dict[str, Any] = json.loads(_json)
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


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    @property
    def score(self) -> int:
        score = 0
        if self.phone and self.email:
            score += 2
        if self.first_name and self.last_name:
            score += 2
        if self.gender and self.birthday:
            score += 2
        return score


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self) -> bool:
        return self.login == ADMIN_LOGIN
