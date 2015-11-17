from pandas.io.pytables import HDFStore

__author__ = 'kepler'


class Store:
    def __init__(self, store_file_path=None):
        self.store_file_path = store_file_path
        self.store = HDFStore(str(store_file_path), mode='a')

    def put(self, name, data_frame):
        self.store.put(name, data_frame, format="table", append=True)

    def get(self, name):
        self.store.get(name)
