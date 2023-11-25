# lasttip
Telegram bot to receive a random album recommendation from my last.fm profile


## Requirements
Python dependencies are listed in the `requirements.txt` file and automatically installed when installing this package with 
`pip install .`.

The following environemntal variables need to be set:

```bash
BOT_TOKEN_DEBUG # The token of the debug bot
DEBUG_CHAT_ID # The id of the debug chat

SPOTIFY_CLIENT_ID # The Spotify API client ID
SPOTIFY_CLIENT_SECRET # The Spotify Client Secret
```

## How to use it
## Telegram bot
```bash
lasttip 
lasttip --production 
```