from lasttip.lasttip import LastTipSuggestion
import shelve
import logging
from typing import List, Iterator


class LastTipHistory:
    """Stores the history of lasttip suggestions in a stack-like structure

    Provides an iterator interface to the history, and functionality to load/save
    the history to a file.

    Args:
        cache_file (str, optional): File to store the history in. Defaults to None.
        max_length (int, optional): Maximum length of the history. Defaults to 10.
    """
    def __init__(self, cache_file: str = None, max_length: int = 10):
        self.max_length = max_length
        self.history = []
        self.save_period = 5
        self.cache_file = cache_file

        if self.cache_file:
            logging.log(logging.INFO, "Loading history from file")
            try:
                with shelve.open(self.cache_file) as d:
                    self.history = d["history"]
            except:
                pass

    def add(self, suggestion: LastTipSuggestion) -> None:
        self.history.append(suggestion)
        if len(self.history) > self.max_length:
            self.history.pop(0)

        if len(self.history) % self.save_period == 0:
            self.save_to_file(self.cache_file)

    def save_to_file(self, cache_file: str) -> None:
        if cache_file:
            logging.log(logging.INFO, "Saving history to file")
            try:
                with shelve.open(cache_file) as d:
                    d["history"] = self.history
            except:
                pass

    def get(self) -> List[LastTipSuggestion]:
        return reversed(self.history)

    def clear_cache(self) -> None:
        self.history = []
        self.save_to_file(self.cache_file)

    # iteration method
    def __iter__(self) -> Iterator[LastTipSuggestion]:
        return iter(self.get())
