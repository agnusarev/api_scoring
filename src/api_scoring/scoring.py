import hashlib

import json
import logging
from tarantool.error import NetworkError

from api_scoring.models import OnlineScoreRequest, ClientsInterestsRequest
from api_scoring.score import cache_get, cache_set, tarantool_get_interests

class GetInterestsException(NetworkError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


def get_key(_online_score_requst: OnlineScoreRequest) -> str:
    key_parts = [
        _online_score_requst.first_name or "",
        _online_score_requst.last_name or "",
        _online_score_requst.phone or "",
        _online_score_requst.birthday.strftime("%d.%m.%Y") or "",  # type: ignore
    ]
    key = "uid:" + hashlib.md5("".join(key_parts).encode("utf-8")).hexdigest()  # type: ignore
    return key


def get_score(_online_score_requst: OnlineScoreRequest) -> float:
    key = get_key(_online_score_requst)
    responce_score = None
    try:
        responce_score = cache_get(key)
    except NetworkError as e:
        logging.exception(f"{e}")

    if responce_score is not None:
        return float(responce_score[1])  # type: ignore

    score = 0.0
    if _online_score_requst.phone:
        score += 1.5
    if _online_score_requst.email:
        score += 1.5
    if _online_score_requst.birthday and _online_score_requst.gender:
        score += 1.5
    if _online_score_requst.first_name and _online_score_requst.last_name:
        score += 0.5
    try:
        cache_set(key, score)
    except NetworkError as e:
        logging.exception(e)
    return score


def get_interests(_clients_interests_request: ClientsInterestsRequest) -> tuple:
    _responce_dict = dict()
    for _client in _clients_interests_request.client_ids:  # type: ignore
        try:
            _responce_dict[_client] = tarantool_get_interests(_client)
        except NetworkError as e:
            logging.exception(e)
            return json.dumps("Can not connect with tarantool."), 500
    return _responce_dict, 200
