# api_scoring

Script run http server and validate requests. Response contains score or list of interests depending on request.

## Installation

````bash
poetry install
````

## Runs

````bash
make run_server
poetry run python src/api_scoring/api.py
````

## Tests

````bash
make test
poetry run pytest tests/
````