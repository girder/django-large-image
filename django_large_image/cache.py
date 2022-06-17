import threading

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from large_image.cache_util.base import BaseCache
from large_image.exceptions import TileCacheConfigurationError


class DjangoCache(BaseCache):
    """Use Django cache as the backing cache for large-image."""

    def __init__(self, cache, alias, getsizeof=None):
        super().__init__(0, getsizeof=getsizeof)
        self._django_cache = cache
        self._alias = alias

    def __repr__(self):  # pragma: no cover
        return f'DjangoCache<{repr(self._alias)}>'

    def __iter__(self):  # pragma: no cover
        # return invalid iter
        return None

    def __len__(self):  # pragma: no cover
        # return invalid length
        return -1

    def __contains__(self, key):
        hashed_key = self._hashKey(key)
        return self._django_cache.__contains__(hashed_key)

    def __delitem__(self, key):
        hashed_key = self._hashKey(key)
        return self._django_cache.delete(hashed_key)

    def __getitem__(self, key):
        hashed_key = self._hashKey(key)
        value = self._django_cache.get(hashed_key)
        if value is None:
            return self.__missing__(key)
        return value

    def __setitem__(self, key, value):
        hashed_key = self._hashKey(key)
        # TODO: do we want to use `add` instead to add a key only if it doesn’t already exist
        return self._django_cache.set(hashed_key, value)

    @property
    def curritems(self):  # pragma: no cover
        raise NotImplementedError

    @property
    def currsize(self):  # pragma: no cover
        raise NotImplementedError

    @property
    def maxsize(self):  # pragma: no cover
        raise NotImplementedError

    def clear(self):
        self._django_cache.clear()

    @staticmethod
    def getCache():  # noqa: N802
        try:
            name = getattr(settings, 'LARGE_IMAGE_CACHE_NAME', 'default')
            dajngo_cache = caches[name]
        except ImproperlyConfigured:  # pragma: no cover
            raise TileCacheConfigurationError
        cache_lock = threading.Lock()
        cache = DjangoCache(dajngo_cache, alias=name)
        return cache, cache_lock
