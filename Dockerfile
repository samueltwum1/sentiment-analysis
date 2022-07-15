FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    git \
    vim

# install poetry
USER root
RUN pip3 install poetry

COPY pyproject.toml poetry.lock* ./

# install runtime dependencies and the app
RUN poetry config virtualenvs.create false && poetry install

RUN ipython profile create
