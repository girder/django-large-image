from large_image.cache_util.base import BaseCache
import pytest

from django_large_image import tilesource
from django_large_image.cache import DjangoCache


@pytest.fixture
def cache_miss_counter():
    class Counter:
        def __init__(self):
            self.count = 0

        def reset(self):
            self.count = 0

    counter = Counter()

    def missing(*args, **kwargs):
        counter.count += 1
        BaseCache.__missing__(*args, **kwargs)

    original = DjangoCache.__missing__
    DjangoCache.__missing__ = missing
    yield counter
    DjangoCache.__missing__ = original


def test_tile(geotiff_path, cache_miss_counter):
    source = tilesource.get_tilesource_from_path(geotiff_path)
    cache_miss_counter.reset()
    # Check size of cache
    _ = source.getTile(0, 0, 0, encoding='PNG')
    assert cache_miss_counter.count == 1
    _ = source.getTile(0, 0, 0, encoding='PNG')
    assert cache_miss_counter.count == 1
