import threading

from large_image.cache_util.base import BaseCache


class DjangoCache(BaseCache):
    """Use Django cache as the backing cache for large-image."""

    def __init__(self, cache, getsizeof=None):
        super().__init__(0, getsizeof=getsizeof)
        self._django_cache = cache

    def __repr__(self):
        return f"DjangoCache: {repr(self._django_cache)}"

    def __iter__(self):
        # return invalid iter
        return None

    def __len__(self):
        # return invalid length
        return -1

    def __contains__(self, key):
        hashedKey = self._hashKey(key)
        return self._django_cache.__contains__(hashedKey)

    def __delitem__(self, key):
        hashedKey = self._hashKey(key)
        return self._django_cache.delete(hashedKey)

    def __getitem__(self, key):
        print(f'getting {key}')
        hashedKey = self._hashKey(key)
        value = self._django_cache.get(hashedKey)
        if value is None:
            return self.__missing__(key)
        return value

    def __setitem__(self, key, value):
        print(f'setting {key}')
        hashedKey = self._hashKey(key)
        # TODO: do we want to use `add` instead to add a key only if it doesn’t already exist
        return self._django_cache.set(hashedKey, value)

    @property
    def curritems(self):
        raise NotImplementedError

    @property
    def currsize(self):
        raise NotImplementedError

    @property
    def maxsize(self):
        raise NotImplementedError

    def clear(self):
        self._django_cache.clear()

    @staticmethod
    def getCache():
        # TODO: may want to try for named cache
        from django.core.cache import cache as django_cache

        cacheLock = threading.Lock()
        cache = DjangoCache(django_cache)
        return cache, cacheLock
