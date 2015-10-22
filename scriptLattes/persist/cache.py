from pathlib import Path

__author__ = 'Kepler'


class Cache:
    def __init__(self):
        self.cache_directory = None
        self.files = {}

    def set_directory(self, cache_directory=None):
        if not cache_directory:
            # do not use any caching
            self.cache_directory = None
            return
        self.cache_directory = Path(cache_directory)
        if not self.cache_directory.exists():
            self.cache_directory.mkdir(parents=True)
        if not self.cache_directory.is_dir():
            raise "'{}' is not a directory".format(self.cache_directory)
        self.cache_directory = self.cache_directory.resolve()

    def new_file(self, file_name):
        if self.cache_directory:
            self.files[file_name] = self.cache_directory / file_name
            return self.files[file_name]
        return None

    @property
    def directory(self):
        return self.cache_directory

    def file(self, file_name):
        return self.files.get(file_name, None)

cache = Cache()
