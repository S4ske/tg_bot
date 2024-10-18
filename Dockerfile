ARG PYTHON_VERSION=3.11.9
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY . .

ENV PYTHONPATH=/app

RUN pip install poetry --no-cache-dir

RUN poetry install --only main --no-interaction

EXPOSE 8000

CMD python telegram/main.py