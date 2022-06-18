# rss_telegram_bot

Simple RSS Telegram bot for daily news fetching.

Fetch one time per day (at 7 AM) all the configured news feeds and then send a summary message to the given chat.

Currently implemented news:

- [MEDIA INAF](https://media.inaf.it)
- [NASA APOD](https://apod.nasa.gov)

## Setup

Create a `mysecrets.py` file with the following content:

```python
BOT_TOKEN: str = ... # your personal telegram bot token
CHAT_ID: int = ... # your telegram chat ID
```

Then you can start it with:

- **Docker**

  ```
  docker compose build --pull --parallel && docker compose up -d
  ```

- **Virtual environment**

  Setup environment:

  ```
  python -m venv venv/
  source venv/bin/activate
  pip install wheel
  pip install -r requirements
  ```

  Start script:

  ```
  python bot.py
  ```
