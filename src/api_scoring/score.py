import logging
from typing import Union, List

import tarantool

TARANTOOL_HOST = "127.0.0.1"
TARANTOOL_PORT = 3302
TARANTOOL_SCORE_SPACE = "scores"
TARANTOOL_INTERESTS_SPACE = "interests"
MAX_ATTEMPTS = 5
SOCKET_TIMEOUT = 10


def cache_get(key: str) -> Union[int, None]:
    conn = tarantool.Connection(  # type: ignore
        host=TARANTOOL_HOST,
        port=TARANTOOL_PORT,
        reconnect_max_attempts=MAX_ATTEMPTS,
        socket_timeout=SOCKET_TIMEOUT,
    )
    response = conn.select(space_name=TARANTOOL_SCORE_SPACE, key=key)
    conn.close()
    if response:
        logging.info(f"{response} was selected from tarantool.")
        return response[0]
    else:
        return None


def cache_set(key: str, value: float) -> None:
    conn = tarantool.Connection(  # type: ignore
        host=TARANTOOL_HOST,
        port=TARANTOOL_PORT,
        reconnect_max_attempts=MAX_ATTEMPTS,
        socket_timeout=SOCKET_TIMEOUT,
    )
    response = conn.insert(space_name=TARANTOOL_SCORE_SPACE, values=(key, value))
    logging.info(f"{response} was inserted in tarantool.")
    conn.close()


def tarantool_get_interests(key: int) -> Union[List[str], None]:
    conn = tarantool.Connection(  # type: ignore
        host=TARANTOOL_HOST,
        port=TARANTOOL_PORT,
        reconnect_max_attempts=MAX_ATTEMPTS,
        socket_timeout=SOCKET_TIMEOUT,
    )
    response = conn.select(space_name=TARANTOOL_INTERESTS_SPACE, key=key)
    conn.close()
    if response:
        logging.info(f"{response} was selected from tarantool.")
        return response[0]
    else:
        return None
