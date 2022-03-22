# flake8: noqa: F401
from django_large_image.rest.data import Data
from django_large_image.rest.metadata import MetaData
from django_large_image.rest.standalone import ListColormapsView, ListTileSourcesView
from django_large_image.rest.tiles import Tiles


class LargeImageView(Data, MetaData, Tiles):
    pass
