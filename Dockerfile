FROM python:3.12 AS python-base

LABEL authors="rshafikov"

COPY requirements* .
RUN pip install -U pip && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/prod/wheels -r requirements.txt
RUN pip install -U pip && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/dev/wheels -r requirements_test.txt


FROM python:3.12 AS prod

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=python-base /usr/src/app/prod/wheels /usr/src/app/wheels
RUN pip install --no-cache /usr/src/app/wheels/*
COPY . .


FROM python:3.12 AS infra

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=python-base /usr/src/app/dev/wheels /usr/src/app/wheels
RUN pip install --no-cache /usr/src/app/wheels/*
COPY . .
