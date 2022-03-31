# flake8: noqa: F401
from functools import wraps

from django_large_image import utilities
from django_large_image.rest.data import Data
from django_large_image.rest.metadata import MetaData
from django_large_image.rest.standalone import ListColormapsView, ListTileSourcesView
from django_large_image.rest.tiles import Tiles


class LargeImageViewMixin(Data, MetaData, Tiles):
    pass


class LargeImageVSIViewMixin(LargeImageViewMixin):
    USE_VSI: bool = True

    @wraps(LargeImageViewMixin.get_path)
    def get_path(self):
        """Wraps get_path with VSI support."""
        field_file = self.get_field_file()
        if self.USE_VSI:
            with utilities.patch_internal_presign(field_file):
                # Grab URL and pass back VSI path
                # DO NOT return here to make sure this context is cleared
                vsi = utilities.make_vsi(field_file.url)
            return vsi
        # Checkout file locally if no VSI
        return LargeImageViewMixin.get_path(self)
