import argparse
import logging
from tokenize import String

import telegram
import telegram.ext

from lasttip.lastfm import Album, LastFm
from lasttip.spotify import Spotify
import os

import dotenv


class TelegramLastFmBot:
    def __init__(self, token: String, lastfm: LastFm, spotify: Spotify):
        self.token = token
        self.lastfm = lastfm
        self.spotify = spotify

        self.updater = telegram.ext.Updater(token=token)
        self.dispatcher = self.updater.dispatcher

        start_handler = telegram.ext.CommandHandler("start", self.start)
        clear_cache_handler = telegram.ext.CommandHandler("clear", self.clear_cache)
        ping_handler = telegram.ext.CommandHandler("ping", self.ping)
        request_handler = telegram.ext.CommandHandler("request", self.request)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(clear_cache_handler)
        self.dispatcher.add_handler(ping_handler)
        self.dispatcher.add_handler(request_handler)

    def request(self, update, context):
        message = update.message.text.replace("/request ", "")

        # context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TelegramLastFmBot.escape(message),
            parse_mode="MarkdownV2",
        )

    def artist(self, update, context):
        message = update.message.text.replace("/artist ", "")
        result = self.spotify.search(message)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TelegramLastFmBot.escape(message),
            parse_mode="MarkdownV2",
        )

    def run(self, webhook=None, port=None):

        if webhook:
            # run on heroku
            logging.info("Running for production using webhooks")
            self.updater.start_webhook(
                listen="0.0.0.0",
                port=port if port else 5000,
                url_path=self.token,
                webhook_url=f"https://lasttip.herokuapp.com/{self.token}",
            )

            self.updater.idle()
        else:
            # run locally
            logging.info("Running locally with polling")
            self.updater.start_polling()

    def ping(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """Ping the bot and see if it is running."""
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm alive")

    @staticmethod
    def escape(msg):
        reserved_chars = ["*", "_", "~", "-", "(", ")", ".", "!"]

        return msg.translate(str.maketrans({c: fr"\{c}" for c in reserved_chars}))

    @staticmethod
    def build_link_msg(text, url):
        message = f"[{TelegramLastFmBot.escape(text)}]({TelegramLastFmBot.escape(url)})"
        return message

    def build_album_message(self, album: Album):
        album_str = str(album)

        logging.debug(f"Random album picked: {album_str}")

        try:
            # remove the dash symbol to get better spotify results
            spotify_query = album_str.replace("-", "")
            album_data = self.spotify.get_album_data(spotify_query)
            url = self.spotify.get_album_url(album_data)

            message = TelegramLastFmBot.build_link_msg(album_str, url)
        except IndexError:
            message = TelegramLastFmBot.escape(album_str)

        return message

    def start(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """Get a random album from my last.fm profile."""

        if not self.lastfm.cached():
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="Building cache first..."
            )

        random_album = self.lastfm.pick_random(playcount_min=10)

        message = self.build_album_message(random_album)

        try:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="MarkdownV2",
            )
        except telegram.error.BadRequest as bad_request:
            logging.error(f"BadRequest: {bad_request.message}")
            logging.error(f"BadRequest: {message}")

        # send a list of alternative albums by the same artist
        albums_msg = ""

        album_list = []
        for (artist_name, uri) in self.spotify.get_artist_uris(random_album.artist):
            for (album_name, album_url) in self.spotify.get_artist_album(uri):

                if album_name not in album_list:
                    album_list.append(album_name)

                    md_text = TelegramLastFmBot.build_link_msg(
                        artist_name + " - " + album_name, album_url
                    )

                    if len(albums_msg) + len(md_text) < 3900 and len(album_list) < 10:
                        albums_msg = albums_msg + "\n\- " + md_text
                    else:
                        break

        if albums_msg:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Here are some other albums by the same artist:"
                + "\n"
                + albums_msg,
                parse_mode="MarkdownV2",
            )

    def clear_cache(
        self, update: telegram.Update, context: telegram.ext.CallbackContext
    ):
        """Clear the last.fm data cache."""
        self.lastfm.clear_cache()
        context.bot.send_media_group(
            chat_id=update.effective_chat.id, text="Clearing cache..."
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", action="store_true")
    args = parser.parse_args()

    dotenv.load_dotenv()

    BOT_TOKEN = os.environ["BOT_TOKEN"]
    LASTFM_USER = os.environ["LASTFM_USER"]
    PORT = os.environ.get("PORT", 5000)
    SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    API_KEY = os.environ["LASTFM_API_KEY"]
    API_SECRET = os.environ["LASTFM_SHARED_SECRET"]

    lastfm = LastFm(LASTFM_USER, API_KEY, API_SECRET)
    spotify = Spotify(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    bot = TelegramLastFmBot(BOT_TOKEN, lastfm, spotify)
    bot.run(webhook=args.production, port=PORT)
