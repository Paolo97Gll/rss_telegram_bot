# syntax=docker/dockerfile:1

# RSS TELEGRAM BOT (https://github.com/Paolo97Gll/rss_telegram_bot)
# Copyright (c) 2022 Paolo Galli

FROM python:3.10

# create venv and export it
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install wheel
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

# update PATH
ENV PATH=/venv/bin:$PATH

# change workdir in "/app" folder
WORKDIR /app
# copy bot app
COPY bot.py .
COPY mysecrets.py .

# exec bot
ENTRYPOINT ["python", "bot.py"]
