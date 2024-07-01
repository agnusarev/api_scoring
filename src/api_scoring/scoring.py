import random
from typing import List

from api_scoring.models import OnlineScoreRequest


def get_score(_online_score_requst: OnlineScoreRequest) -> float:
    score = 0.0
    if _online_score_requst.phone:
        score += 1.5
    if _online_score_requst.email:
        score += 1.5
    if _online_score_requst.birthday and _online_score_requst.gender:
        score += 1.5
    if _online_score_requst.first_name and _online_score_requst.last_name:
        score += 0.5
    return score


def get_interests() -> List[str]:
    interests = [
        "cars",
        "pets",
        "travel",
        "hi-tech",
        "sport",
        "music",
        "books",
        "tv",
        "cinema",
        "geek",
        "otus",
    ]
    return random.sample(interests, 2)
