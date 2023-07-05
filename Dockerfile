FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat-traditional
RUN python3 -m pip install -U pip poetry
RUN poetry config virtualenvs.create false

RUN mkdir /answerly
WORKDIR /answerly
COPY README.md .
COPY poetry.lock pyproject.toml .
RUN poetry install --no-dev

COPY asnwerly .

ENTRYPOINT ["/answerly/entrypoint.sh"]
