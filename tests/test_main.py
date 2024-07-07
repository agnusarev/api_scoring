import pytest

from api_scoring.api import FORBIDDEN, OK, get_token, method_handler
from api_scoring.models import MethodRequest
from unittest.mock import Mock


@pytest.mark.parametrize(
    "_request,_expected,_code",
    [
        pytest.param(
            {
                "body": {
                    "account": "horns&hoofs",
                    "login": "h&f",
                    "method": "online_score",
                    "token": "",
                    "arguments": {
                        "phone": "79175002040",
                        "email": "stupnikov@otus.ru",
                        "first_name": "Stanislav",
                        "last_name": "Stupnikov",
                        "birthday": "01.01.1990",
                        "gender": 1,
                    },
                }
            },
            {"score": 5.0},
            OK,
            id="test_main_autentification",
        ),
        pytest.param(
            {
                "body": {
                    "account": "horns&hoofs",
                    "login": "admin",
                    "method": "online_score",
                    "token": "",
                    "arguments": {
                        "phone": "79175002040",
                        "email": "stupnikov@otus.ru",
                        "first_name": "Stanislav",
                        "last_name": "Stupnikov",
                        "birthday": "01.01.1990",
                        "gender": 1,
                    },
                }
            },
            {"score": 42},
            OK,
            id="test_admin_autentification",
        ),
    ],
)
def test_online_score(_request: dict, _expected: str, _code: int) -> None:
    _request["body"]["token"] = get_token(MethodRequest(_request["body"]))
    _exp, _cod = method_handler(_request, dict(), "")
    assert _cod == _code
    assert _exp == _expected


@pytest.mark.parametrize(
    "_request,_code,_returns",
    [
        pytest.param(
            {
                "body": {
                    "account": "horns&hoofs",
                    "login": "h&h",
                    "method": "online_score",
                    "token": "",
                    "arguments": {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"},
                }
            },
            OK,
            ["cats", "dogs", "otus", "programming"],
            id="test_main_autentification",
        ),
    ],
)
def test_clients_interests(_request: dict, _code: int, _returns: list) -> None:
    _request["body"]["token"] = get_token(MethodRequest(_request["body"]))
    method_handler = Mock()
    method_handler.return_value = _returns, OK
    _exp, code = method_handler(_request, dict(), "")
    assert code == _code
    assert len(_request["body"]["arguments"]["client_ids"]) == len(_exp)


@pytest.mark.parametrize(
    "_request,_code",
    [
        pytest.param(
            {
                "body": {
                    "account": "horns&hoofs",
                    "login": "admin",
                    "method": "online_score",
                    "token": "sfsfsf",
                    "arguments": {
                        "phone": "79175002040",
                        "email": "stupnikov@otus.ru",
                        "first_name": "Stanislav",
                        "last_name": "Stupnikov",
                        "birthday": "01.01.1990",
                        "gender": 2,
                    },
                }
            },
            FORBIDDEN,
        ),
    ],
)
def test_wrong_autentification(_request: dict, _code: int) -> None:
    _, code = method_handler(_request, dict(), "")
    assert code == _code
