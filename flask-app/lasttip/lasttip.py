import lasttip.lastfm
import lasttip.spotify


from dataclasses import dataclass


@dataclass
class LastTipSuggestion:
    album_name: str
    album_artist: str
    playcount: int
    url: str
    image: str
    spotify_data: str
    artist_url: str


class LastTip:
    def __init__(self, lastfm: lasttip.lastfm.LastFm, spotify: lasttip.spotify.Spotify):
        self.lastfm = lastfm
        self.spotify = spotify
        self.query_strategy = lasttip.spotify.BasicSpotifyQuery()

    def get_suggestion(self, playcount_min=10, limit=10) -> LastTipSuggestion:
        album = self.lastfm.pick_random(playcount_min=10)
        try:
            # remove the dash symbol to get better spotify results
            result = self.query_strategy.query(spotify=self.spotify, album=album)
            suggestion = LastTipSuggestion(
                album_name=album.name,
                album_artist=album.artist,
                url=result.album_url,
                image=result.image_url,
                spotify_data=result.search_data,
                artist_url=result.artist_url,
                playcount=album.playcount,
            )

            return suggestion

        except IndexError:
            return LastTipSuggestion(album, None, None, None, None)
