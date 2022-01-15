import argparse
import logging

import telegram
import telegram.ext

from lastfm import LastFm
from spotify import Spotify
import os

parser = argparse.ArgumentParser()
parser.add_argument("--production", action="store_true")
args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
LASTFM_USER = os.environ["LASTFM_USER"]
PORT = os.environ.get("PORT", 5000)

updater = telegram.ext.Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher

lastfm = LastFm(LASTFM_USER)
spotify = Spotify()


def ping(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Ping the bot and see if it is running."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm alive")


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Get a random album from my last.fm profile."""

    if not lastfm.cached():
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Building cache first..."
        )

    random_album = str(lastfm.pick_random(playcount_min=20))
    try:
        message = spotify.get_url(random_album)
    except IndexError:
        message = random_album

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def clear_cache(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Clear the last.fm data cache."""
    lastfm.clear_cache()
    context.bot.send_media_group(
        chat_id=update.effective_chat.id, text="Clearing cache..."
    )


if __name__ == "__main__":
    start_handler = telegram.ext.CommandHandler("start", start)
    clear_cache_handler = telegram.ext.CommandHandler("clear", clear_cache)
    ping_handler = telegram.ext.CommandHandler("ping", ping)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(clear_cache_handler)
    dispatcher.add_handler(ping_handler)

    if args.production:
        # run on heroku
        logging.info("Running for production using webhooks")
        updater.start_webhook(
            listen="0.0.0.0",
            port=int(PORT),
            url_path=BOT_TOKEN,
            webhook_url=f"https://lasttip.herokuapp.com/{BOT_TOKEN}",
        )

        updater.idle()
    else:
        # run locally
        logging.info("Running locally with polling")
        updater.start_polling()
