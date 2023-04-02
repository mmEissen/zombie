FROM python:3.11

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.4.1

RUN apt-get update && apt-get install -y \
  python3-dev \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN touch README.md

RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi --no-root

COPY zombie/ /code/zombie/

RUN poetry install --only main --no-interaction --no-ansi

ENTRYPOINT [ "python", "-m", "zombie.server" ]
