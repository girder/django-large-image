from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution('django-large-image').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = ''
