import random
from datetime import datetime
from typing import Any, Union, List


def get_score(
    store: float,
    phone: str,
    email: str,
    birthday: Union[datetime, None] = None,
    gender: Union[int, None] = None,
    first_name: Union[str, None] = None,
    last_name: Union[str, None] = None,
) -> float:
    score = 0.0
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    return score


def get_interests(store: Any, cid: Any) -> List[str]:
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
