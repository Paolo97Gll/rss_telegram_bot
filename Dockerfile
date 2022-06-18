# syntax=docker/dockerfile:1

# RSS TELEGRAM BOT (https://github.com/Paolo97Gll/rss_telegram_bot)
# Copyright (c) 2022 Paolo Galli

ARG PYTHON_VERSION=3.10

##############
## BUILD-VENV

FROM python:${PYTHON_VERSION} AS build-venv

# create venv and export it
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

#########
## FINAL

FROM python:${PYTHON_VERSION}-slim AS final

# set timezone
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# copy venv
COPY --from=build-venv /venv /venv
ENV PATH=/venv/bin:$PATH

# change workdir in "/app" folder
WORKDIR /app
# copy bot app
COPY bot.py .
COPY mysecrets.py .

# exec bot
ENTRYPOINT ["python", "bot.py"]
