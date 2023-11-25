import lasttip.lastfm as lastfm
import lasttip.spotify as spotify


from dataclasses import dataclass


@dataclass
class LastTipSuggestion:
    album: lastfm.Album
    url: str
    image: str
    spotify_data: str


class LastTip:
    def __init__(self, lastfm: lastfm.LastFm, spotify: spotify.Spotify):
        self.lastfm = lastfm
        self.spotify = spotify

    def get_suggestion(self, playcount_min=10, limit=10) -> LastTipSuggestion:
        album = self.lastfm.pick_random(playcount_min=10)
        album_str = str(album)

        try:
            # remove the dash symbol to get better spotify results
            spotify_query = album_str.replace("-", "")
            album_data = self.spotify.get_album_data(spotify_query)

            image = self.spotify.get_album_image(album_data)
            url = self.spotify.get_album_url(album_data)
            return LastTipSuggestion(album, url, image, album_data)

        except IndexError:
            return LastTipSuggestion(album, None, None)
