import pytest

from api_scoring.models import (
    ClientsInterestsRequest,
    MethodRequest,
    OnlineScoreRequest,
)


@pytest.mark.parametrize(
    "_attr_dict",
    [
        {"client_ids": [1, 2, 3], "date": "10.10.2024"},
        {"client_ids": [11, 4, 5], "date": "01.01.2020"},
    ],
)
def test_clients_interests_request_success(_attr_dict: dict) -> None:
    assert ClientsInterestsRequest(_attr_dict)


def test_clients_interests_request_requered_attributes() -> None:
    with pytest.raises(ValueError, match=r"Attribute client_ids must be pass in*"):
        ClientsInterestsRequest({"date": "10.10.2024"})


@pytest.mark.parametrize(
    "_attr_dict",
    [
        {"client_ids": 10, "date": "10.10.2024"},
        {"client_ids": [11, 4, 5], "date": "01.01.20"},
        {"client_ids": "wrong_str", "date": "01.01.2024"},
        {"client_ids": {"wrong_id": 123}, "date": "01.01.2024"},
    ],
)
def test_clients_interests_request_failed(_attr_dict: dict) -> None:
    with pytest.raises(ValueError):
        ClientsInterestsRequest(_attr_dict)


@pytest.mark.parametrize(
    "_attr_dict",
    [
        {
            "phone": "79175002040",
            "email": "stupnikov@otus.ru",
            "first_name": "Stanislav",
            "last_name": "Stupnikov",
            "birthday": "01.01.1990",
            "gender": 1,
        },
        {
            "phone": "78175002045",
            "email": "gnusarev@otus.ru",
            "first_name": "Alexander",
            "last_name": "Gnusarev",
            "birthday": "05.10.1990",
            "gender": 2,
        },
        {
            "phone": 78175002045,
            "email": "gnusarev@otus.ru",
            "first_name": "Alexander",
            "last_name": "Gnusarev",
            "birthday": "05.10.1990",
            "gender": 2,
        },
    ],
)
def test_online_score_request_success(_attr_dict: dict) -> None:
    assert OnlineScoreRequest(_attr_dict)


@pytest.mark.parametrize(
    "_attr_dict, _error",
    [
        (
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "first_name": "Stanislav",
                "last_name": "Stupnikov",
                "birthday": "01.01.1990",
                "gender": 4,
            },
            r"Invalid gender: 4. Gender must be 0, 1 or 2.",
        ),
        (
            {
                "phone": "98175002045",
                "email": "gnusarev@otus.ru",
                "first_name": "Alexander",
                "last_name": "Gnusarev",
                "birthday": "05.10.1990",
                "gender": 2,
            },
            r"Invalid phone number: 98175002045. Phone must start with 7.",
        ),
        (
            {
                "phone": "781750020451",
                "email": "gnusarev@otus.ru",
                "first_name": "Alexander",
                "last_name": "Gnusarev",
                "birthday": "05.10.1990",
                "gender": 2,
            },
            r"Invalid phone number: 781750020451. Phone must have 11 digits.",
        ),
        (
            {
                "phone": ["781750020451"],
                "email": "gnusarev@otus.ru",
                "first_name": "Alexander",
                "last_name": "Gnusarev",
                "birthday": "05.10.1990",
                "gender": 2,
            },
            r"Invalid type for phone number*",
        ),
        (
            {
                "phone": "78175002045",
                "email": "gnusarevotus.ru",
                "first_name": "Alexander",
                "last_name": "Gnusarev",
                "birthday": "05.10.1990",
                "gender": 2,
            },
            r"gnusarevotus.ru isn't valid email.",
        ),
        (
            {
                "phone": "78175002045",
                "email": "gnusarev@otus.ru",
                "first_name": "Alexander",
                "last_name": "Gnusarev",
                "birthday": "05.10.1910",
                "gender": 2,
            },
            r"Invalid birthday: 1910-10-05 00:00:00. Difference between current date is too long.",
        ),
    ],
)
def test_online_score_request_failed(_attr_dict: dict, _error: str) -> None:
    with pytest.raises(ValueError, match=_error):
        OnlineScoreRequest(_attr_dict)


@pytest.mark.parametrize(
    "_attr_dict,_score",
    [
        (
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "first_name": "Stanislav",
                "last_name": "Stupnikov",
                "birthday": "01.01.1990",
                "gender": 1,
            },
            6,
        ),
        (
            {
                "phone": "78175002045",
                "email": "gnusarev@otus.ru",
                "first_name": "Stanislav",
            },
            2,
        ),
        (
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "birthday": "01.01.1990",
                "gender": 1,
            },
            4,
        ),
    ],
)
def test_online_score_request_score(_attr_dict: dict, _score: int) -> None:
    _online_score_request = OnlineScoreRequest(_attr_dict)
    assert _online_score_request.score == _score


@pytest.mark.parametrize(
    "_attr_dict",
    [
        {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "token": "d3573aff1555c",
            "arguments": {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "first_name": "Stanislav",
                "last_name": "Stupnikov",
                "birthday": "01.01.1990",
                "gender": 1,
            },
        },
        {
            "login": "gnusarev",
            "method": "online_score",
            "token": "d3573aff1555c",
            "arguments": {
                "phone": "79177802040",
                "email": "stupnikov@otus.ru",
                "first_name": "Alexander",
                "last_name": "Gnusarev",
                "birthday": "05.08.1989",
                "gender": 2,
            },
        },
    ],
)
def test_method_request_success(_attr_dict: dict) -> None:
    assert MethodRequest(_attr_dict)


@pytest.mark.parametrize(
    "_attr_dict,_error",
    [
        (
            {
                "account": "horns&hoofs",
                "method": "online_score",
                "token": "d3573aff1555c",
                "arguments": {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "first_name": "Stanislav",
                    "last_name": "Stupnikov",
                    "birthday": "01.01.1990",
                    "gender": 1,
                },
            },
            r"Attribute login must be pass in*",
        ),
        (
            {
                "login": "gnusarev",
                "method": "online_score",
                "arguments": {
                    "phone": "79177802040",
                    "email": "stupnikov@otus.ru",
                    "first_name": "Alexander",
                    "last_name": "Gnusarev",
                    "birthday": "05.08.1989",
                    "gender": 2,
                },
            },
            r"Attribute token must be pass in*",
        ),
    ],
)
def test_method_requests_requered_attributes(_attr_dict: dict, _error: str) -> None:
    with pytest.raises(ValueError, match=_error):
        MethodRequest(_attr_dict)


@pytest.mark.parametrize(
    "_attr_dict,_error",
    [
        (
            {
                "login": "gnusarev",
                "account": 456,
                "method": "online_score",
                "token": "d3573aff1555c",
                "arguments": {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "first_name": "Stanislav",
                    "last_name": "Stupnikov",
                    "birthday": "01.01.1990",
                    "gender": 1,
                },
            },
            r"CharField must be str",
        ),
        (
            {
                "login": "gnusarev",
                "method": "online_score",
                "token": "d3573aff1555c",
                "arguments": "arguments",
            },
            r"ArgumentsField must be dict",
        ),
    ],
)
def test_method_requests_failed(_attr_dict: dict, _error: str) -> None:
    with pytest.raises(ValueError, match=_error):
        MethodRequest(_attr_dict)
