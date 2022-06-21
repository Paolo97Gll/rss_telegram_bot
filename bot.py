#!/usr/bin/env python3.10

# RSS TELEGRAM BOT (https://github.com/Paolo97Gll/rss_telegram_bot)
# Copyright (c) 2022 Paolo Galli

import asyncio
import logging
import os
from datetime import datetime, timedelta

import aiogram.utils.markdown as md
import ujson
import uvloop
import xmltodict
from aiogram import Bot
from aiohttp import ClientSession, ClientTimeout
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from mysecrets import * # for BOT_TOKEN, CHAT_ID and TIMEZONE


#####################################################################
# BASIC CONFIGURATION


logging_format = "[%(asctime)s] (%(levelname)s) %(module)s - %(funcName)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=logging_format)

class ColoredFormatter(logging.Formatter):
    """ Colored formatter for the logging package. """

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *, defaults=None):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        colors = {
            "red": "\x1b[31;20m", "bold_red": "\x1b[31;1m",
            "green": "\x1b[32;20m", "bold_green": "\x1b[32;1m",
            "yellow": "\x1b[33;20m", "bold_yellow": "\x1b[33;1m",
            "blue": "\x1b[34;20m", "bold_blue": "\x1b[34;1m",
            "grey": "\x1b[37;20m", "bold_grey": "\x1b[37;1m",
            "reset": "\x1b[0m"
        }
        self._default_formatter = logging.Formatter(fmt)
        self._formatters = {
            1: logging.Formatter(colors["bold_blue"] + fmt + colors["reset"]),
            logging.DEBUG: logging.Formatter(colors["grey"] + fmt + colors["reset"]),
            logging.INFO: logging.Formatter(colors["green"] + fmt + colors["reset"]),
            logging.WARNING: logging.Formatter(colors["yellow"] + fmt + colors["reset"]),
            logging.ERROR: logging.Formatter(colors["red"] + fmt + colors["reset"]),
            logging.CRITICAL: logging.Formatter(colors["bold_red"] + fmt + colors["reset"])
        }

    def format(self, record):
        return self._formatters.get(record.levelno, self._default_formatter).format(record)

(logger := logging.getLogger(__name__)).setLevel(1)
logger.propagate = False
(logger_handler := logging.StreamHandler()).setFormatter(ColoredFormatter(fmt=logging_format))
logger.addHandler(logger_handler)

timezone_tmp = os.getenv("TZ")
if not timezone_tmp:
    logger.warning("Timezone is None, setting to Etc/UTC")
TIMEZONE = timezone_tmp if timezone_tmp else "Etc/UTC"

BOT = Bot(BOT_TOKEN)

class Utils():
    """ Utility class for requests. """

    def __init__(self) -> None:
        self._session = None

    async def create_session(self) -> None:
        self._session = ClientSession(json_serialize=ujson.dumps, timeout=ClientTimeout(total=5))

    async def close_session(self) -> None:
        await self._session.close()
        self._session = None

    async def fetch(self, url: str) -> str:
        if self._session is None:
            logger.warning("Session not created, creating")
            await self.create_session()
        try:
            async with self._session.get(url) as response:
                rsp = await response.text()
            return rsp
        except Exception as e:
            logger.error(f"Cannot connect with {url}")
            logger.error(f"{type(e).__name__}: {e}")
            return None

utils = Utils()


#####################################################################
# SCHEDULER


async def fetch_news_feed(date, dt_low, dt_high) -> bool:
    try:
        msg = f"RIASSUNTO NEWS DEL {date}"
        msg = f"{md.bold(msg)}\n\n"
        # FETCH MEDIA INAF
        rsp = await utils.fetch("http://media.inaf.it/feed")
        rsp = xmltodict.parse(rsp)["rss"]["channel"]
        items = [i for i in range(len(rsp["item"]))
            if dt_low < datetime.strptime(rsp["item"][i]["pubDate"], "%a, %d %b %Y %H:%M:%S +0000") < dt_high]
        msg += f"{md.bold(rsp['title'])}\n{md.italic(rsp['description'])}\n{md.escape_md(rsp['link'])}\n"
        if items:
            for i in items:
                msg += f"\n• {md.link(rsp['item'][i]['title'], rsp['item'][i]['link'])}"
        else:
            msg += "\nNon ci sono news per questa giornata"
        # SEND MESSAGE
        await BOT.send_message(CHAT_ID, msg, "MarkdownV2", disable_web_page_preview=True)
        return True
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        return False

async def fetch_news_apod(date, dt_low, dt_high) -> bool:
    try:
        rsp = await utils.fetch(f"https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&date={dt_low.strftime('%Y-%m-%d')}")
        rsp = ujson.loads(rsp)
        apod_date = f"APOD {date}"
        apod_page_link = f"https://apod.nasa.gov/apod/ap{dt_low.strftime('%y%m%d')}.html"
        msg = f"{md.link(apod_date, apod_page_link)}: \"{rsp['title']}\""
        await BOT.send_photo(CHAT_ID, rsp["url"], msg, "MarkdownV2")
        return True
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        return False


scheduler = AsyncIOScheduler(timezone=TIMEZONE)

@scheduler.scheduled_job(CronTrigger(hour=7))
# @scheduler.scheduled_job(IntervalTrigger(seconds=5)) # for debug
async def fetch_news():
    date = (datetime.now()-timedelta(days=1)).strftime('%d/%m/%Y')
    dt_high = datetime.now()
    dt_low = dt_high - timedelta(days=1)
    status_feed, status_apod = False, False
    for _ in range(48):
        if not status_feed:
            status_feed = await fetch_news_feed(date, dt_low, dt_high)
        if not status_apod:
            status_apod = await fetch_news_apod(date, dt_low, dt_high)
        if status_feed and status_apod:
            return
        asyncio.sleep(300)


#####################################################################


async def main():
    scheduler.start()
    await utils.create_session()
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        logger.log(1, "[MAIN] Starting app: rss_telegram_bot")
        uvloop.install()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.log(1, "[MAIN] Interrupt detected, exit")
        asyncio.run(utils.close_session())
