# flake8: noqa: F401
from functools import wraps

from rest_framework.exceptions import APIException
from rest_framework.request import Request

from django_large_image import utilities
from django_large_image.rest.data import DataMixin
from django_large_image.rest.metadata import MetaDataMixin
from django_large_image.rest.standalone import ListColormapsView, ListTileSourcesView
from django_large_image.rest.tiles import TilesMixin


class BaseLargeImageViewMixin(DataMixin, MetaDataMixin, TilesMixin):
    """Abstract class for large-image endpoints.

    Subclasses must implement `get_path()`:

    .. code:: python

        def get_path(self, request: Request, pk: int):
            instance = Model.objects.get(pk=pk)
            return instance.file.name

    """

    pass


class LargeImageViewSetMixin(BaseLargeImageViewMixin):
    """Mixin specifically for ViewSets that have a file field on the mdoel.

    Define `FILE_FIELD_NAME` as the string name of the file field on the
    subclassed ViewSet's model.

    This mixin assumes `get_object()` is present - thus for ViewSets
    """

    FILE_FIELD_NAME: str = None

    def get_field_file(self):
        """Get `FileField` using `FILE_FIELD_NAME`."""
        try:
            return getattr(self.get_object(), self.FILE_FIELD_NAME)
        except (AttributeError, TypeError):
            # Raise 500 server error
            raise APIException('`FILE_FIELD_NAME` not properly set on viewset class.')

    @wraps(BaseLargeImageViewMixin.get_path)
    def get_path(self, request: Request, pk: int):
        return utilities.field_file_to_local_path(self.get_field_file())


class LargeImageVSIViewSetMixin(LargeImageViewSetMixin):
    USE_VSI: bool = True

    @wraps(LargeImageViewSetMixin.get_path)
    def get_path(self, request: Request, pk: int):
        """Wraps get_path with VSI support."""
        field_file = self.get_field_file()
        if self.USE_VSI:
            with utilities.patch_internal_presign(field_file):
                # Grab URL and pass back VSI path
                # DO NOT return here to make sure this context is cleared
                vsi = utilities.make_vsi(field_file.url)
            return vsi
        # Checkout file locally if no VSI
        return LargeImageViewSetMixin.get_path(self, request, pk)
