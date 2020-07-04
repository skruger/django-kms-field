from collections import OrderedDict


class SimpleCache:
    class CacheMiss(Exception):
        pass

    def __init__(self, max_size=100):
        self.max_size = max_size
        self._cache = OrderedDict()

    def __len__(self):
        return len(self._cache)

    def set(self, key, item):
        if len(self._cache.keys()) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = item

    def get(self, key):
        try:
            return self._cache[key]
        except KeyError:
            raise self.CacheMiss()
