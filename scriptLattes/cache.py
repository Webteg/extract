from pathlib import Path

__author__ = 'Kepler'


class Cache:
    def __init__(self):
        self.cache_directory = None

    def set_directory(self, cache_directory=None):
        if not cache_directory:
            # do not use any caching
            self.cache_directory = None
            return
        self.cache_directory = Path(cache_directory)
        if not self.cache_directory.exists():
            self.cache_directory.mkdir(parents=True)

    @property
    def directory(self):
        return self.cache_directory

cache = Cache()
