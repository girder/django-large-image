from contextlib import contextmanager

from large_image.cache_util.base import BaseCache
import pytest

from django_large_image import tilesource
from django_large_image.cache import DjangoCache


@contextmanager
def cache_tracker():
    cache, _ = DjangoCache.getCache()
    cache.clear()

    class Counter:
        def __init__(self):
            self.reset()
            self.cache = cache

        def reset(self):
            self.count = 0
            self.keys = set()

    counter = Counter()

    def missing(self, key, *args, **kwargs):
        counter.count += 1
        counter.keys.add(key)
        BaseCache.__missing__(self, key, *args, **kwargs)

    original = DjangoCache.__missing__
    DjangoCache.__missing__ = missing
    yield counter
    DjangoCache.__missing__ = original


def test_cache_tile(geotiff_path):
    source = tilesource.get_tilesource_from_path(geotiff_path)
    with cache_tracker() as tracker:
        _ = source.getTile(0, 0, 0, encoding='PNG')
        assert tracker.count == 1
        _ = source.getTile(0, 0, 0, encoding='PNG')
        assert tracker.count == 1


def test_cache_access(geotiff_path):
    source = tilesource.get_tilesource_from_path(geotiff_path)
    with cache_tracker() as tracker:
        _ = source.getTile(0, 0, 0, encoding='PNG')
        assert tracker.count == 1
        assert all([k in tracker.cache for k in tracker.keys])
        for k in tracker.keys:
            del tracker.cache[k]
        assert all([k not in tracker.cache for k in tracker.keys])
        _ = source.getTile(0, 0, 0, encoding='PNG')
        assert tracker.count == 2
        assert len(tracker.keys) == 1
