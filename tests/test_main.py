import datetime
import hashlib

import pytest

from api_scoring.api import method_handler


def set_valid_auth(request: dict) -> str:
    _token = None
    if request["body"].get("login") == "admin":
        _token = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + "42").encode("utf-8")
        ).hexdigest()
    else:
        msg = (
            request["body"].get("account", "")
            + request["body"].get("login", "")
            + "Otus"
        ).encode("utf-8")
        _token = hashlib.sha512(msg).hexdigest()
    return _token


@pytest.mark.parametrize(
    "_request,_ctx,_store,_expected,_code",
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
            dict(),
            "",
            {"score": 5.0},
            200,
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
            dict(),
            "",
            {"score": 42},
            200,
            id="test_admin_autentification",
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
                        "gender": 4,
                    },
                }
            },
            dict(),
            "",
            "",
            400,
            id="test_wrong_gender",
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            {
                "body": {
                    "account": "horns&hoofs",
                    "login": "admin",
                    "method": "online_score",
                    "token": "",
                    "arguments": {
                        "phone": "89175002040",
                        "email": "stupnikov@otus.ru",
                        "first_name": "Stanislav",
                        "last_name": "Stupnikov",
                        "birthday": "01.01.1990",
                        "gender": 4,
                    },
                }
            },
            dict(),
            "",
            "",
            400,
            id="test_wrong_phone",
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_online_score(_request: dict, _ctx: dict, _store: str, _expected: str, _code: int) -> None:
    _request["body"]["token"] = set_valid_auth(_request)
    _exp, _cod = method_handler(_request, _ctx, _store)
    assert _cod == _code
    assert _exp == _expected


@pytest.mark.parametrize(
    "_request,_ctx,_store,_code",
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
            dict(),
            "",
            200,
            id="test_main_autentification",
        ),
    ],
)
def test_clients_interests(_request: dict, _ctx: dict, _store: str, _code: int) -> None:
    _request["body"]["token"] = set_valid_auth(_request)
    _exp, _cod = method_handler(_request, _ctx, _store)
    assert _cod == _code
    assert len(_request["body"]["arguments"]["client_ids"]) == len(_exp)
