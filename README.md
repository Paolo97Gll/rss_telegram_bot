# rss_telegram_bot

Simple RSS Telegram bot for daily news fetching.

Fetch one time per day (at 7 AM) all the configured news feeds and then send a summary message to the given chat.

Currently implemented news:

- [MEDIA INAF](https://media.inaf.it)
- [NASA APOD](https://apod.nasa.gov)

## Customizations

All customizations should be placed in the `fetch_news*` functions, that are the core of the bot. Change their implementation according to your preferences (you can change the news sources, the message formatting, ...).

To change the scheduling, simply change the decorators on top of the function. For example, if you want to receive news every day at 7 AM and 7 PM:

```python
@scheduler.scheduled_job(CronTrigger(hour=7))
@scheduler.scheduled_job(CronTrigger(hour=19))
async def fetch_news(...):
  ...
```

More informations about the existing triggers in the [APScheduler documentation](https://apscheduler.readthedocs.io/en/3.x/userguide.html#choosing-the-right-scheduler-job-store-s-executor-s-and-trigger-s).

To change timezone, change the `TZ` environment variable in Dockerfile, for example:

```Dockerfile
ENV TZ=Europe/Rome
```

```Dockerfile
ENV TZ=America/New_York
```

```Dockerfile
ENV TZ=Etc/UTC
```

## Setup

Create a `mysecrets.py` file with the following content:

```python
BOT_TOKEN: str = ... # your personal telegram bot token
CHAT_ID_LIST_FEED: list[int] = [...] # your telegram chat IDs for feed news
CHAT_ID_LIST_APOD: list[int] = [...] # your telegram chat IDs for apod news
```

Then you can start it with:

- **Docker**

  ```
  docker compose build --pull && docker compose up -d
  ```

- **Virtual environment**

  Setup environment:

  ```
  python -m venv venv
  source venv/bin/activate
  pip install wheel
  pip install -r requirements
  ```

  Start script:

  ```
  python bot.py
  ```
