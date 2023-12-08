import logging
from tokenize import String
from asyncio import Queue
import telegram
import telegram.ext
from telegram.ext import Updater, Application
from telegram import Update
import requests
from typing import Callable

import os


class BackendInterface:
    def __init__(self, url) -> None:
        self.url = url

    def send_request(self, url):
        logging.info(f"Sending request to {url}")
        return requests.get(url).json()

    def index(self):
        logging.info("Fetching random album from index")
        return self.send_request(self.url + "/json")

    def lastfm(self):
        logging.info("Fetching random album from lastfm")
        return self.send_request(self.url + "/lastfm_json")

    def spotify(self):
        logging.info("Fetching random album from spotify")
        return self.send_request(self.url + "/spotify_json")


class TelegramLastFmBot:
    def __init__(self, token: String, backend: BackendInterface):
        self.token = token
        self.backend = backend
        self.queue: Queue = Queue()
        self.bot: telegram.Bot = telegram.Bot(token=token)

        self.updater: Updater = telegram.ext.Updater(self.bot, self.queue)

        self.application = Application.builder().token(token).build()

        start_handler = telegram.ext.CommandHandler(
            "start", lambda x, y: self.start(x, y, self.backend.index)
        )
        lastfm_handler = telegram.ext.CommandHandler(
            "lastfm", lambda x, y: self.start(x, y, self.backend.lastfm)
        )
        spotify_handler = telegram.ext.CommandHandler(
            "spotify", lambda x, y: self.start(x, y, self.backend.spotify)
        )
        request_handler = telegram.ext.CommandHandler("request", self.request)

        self.application.add_handler(start_handler)
        self.application.add_handler(request_handler)
        self.application.add_handler(lastfm_handler)
        self.application.add_handler(spotify_handler)

    async def request(self, update, context):
        message = update.message.text.replace("/request ", "")

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TelegramLastFmBot.escape(message),
            parse_mode="MarkdownV2",
        )

    def run(self, port: int = None):
        # run locally
        logging.info("Running locally with polling")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def ping(
        self, update: telegram.Update, context: telegram.ext.CallbackContext
    ):
        """Ping the bot and see if it is running."""
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm alive")

    @staticmethod
    def escape(msg):
        reserved_chars = ["*", "_", "~", "-", "(", ")", ".", "!", "+"]

        return msg.translate(str.maketrans({c: rf"\{c}" for c in reserved_chars}))

    @staticmethod
    def build_link_msg(text, url):
        message = f"[{TelegramLastFmBot.escape(text)}]({TelegramLastFmBot.escape(url)})"
        return message

    def build_album_message(self, album):
        album_name = album["album_name"]
        album_artist = album["album_artist"]
        album_str = f"{album_artist} - {album_name}"
        url = album["url"]

        logging.debug(f"Random album picked: {album_str}")

        if url:
            message = TelegramLastFmBot.build_link_msg(album_str, url)
        else:
            message = TelegramLastFmBot.escape(album_str)

        return message

    async def start(
        self,
        update: telegram.Update,
        context: telegram.ext.CallbackContext,
        api_call: Callable,
    ):
        """Get a random album from my last.fm profile."""

        logging.info("Fetching random album")

        try:
            album = api_call()
            message = self.build_album_message(album)
            message += (
                "\n\nYou can request a new album with /start, /lastfm or /spotify"
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="MarkdownV2",
            )

        except telegram.error.BadRequest as bad_request:
            logging.error(f"BadRequest: {bad_request.message}")
            logging.error(f"BadRequest: {message}")

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"BadRequest: {bad_request.message}",
            )
        except Exception as e:
            logging.error(f"Exception: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Exception: {e}",
            )


def entry_point():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    PORT = 8443
    BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
    API_URL = os.environ.get("LASTTIP_API_URL")

    api = BackendInterface(API_URL)
    bot = TelegramLastFmBot(BOT_TOKEN, api)
    bot.run(port=PORT)


def main():
    # asyncio.run(entry_point())
    entry_point()


if __name__ == "__main__":
    main()
