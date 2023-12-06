import lasttip.lastfm
import lasttip.spotify
from lasttip.recommender import AlbumSuggestion
from lasttip.recommender import Recommender





class LastTip(Recommender):
    def __init__(self, lastfm: lasttip.lastfm.LastFm, spotify: lasttip.spotify.Spotify):
        self.lastfm = lastfm
        self.spotify = spotify
        self.query_strategy = lasttip.spotify.BasicSpotifyQuery()

    def get_suggestion(self, playcount_min=10, limit=10) -> AlbumSuggestion:
        album = self.lastfm.pick_random(playcount_min=10)
        try:
            # remove the dash symbol to get better spotify results
            result = self.query_strategy.query(spotify=self.spotify, album=album)
            suggestion = AlbumSuggestion(
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
            return AlbumSuggestion(album, None, None, None, None)
