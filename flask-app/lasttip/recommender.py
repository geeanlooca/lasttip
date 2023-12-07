from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class AlbumSuggestion:
    album_name: str
    album_artist: str
    playcount: int
    url: str
    image: str
    spotify_data: str
    artist_url: str


class Recommender(ABC):
    @abstractmethod
    def get_suggestion(self, *args, **kwargs) -> AlbumSuggestion:
        pass
