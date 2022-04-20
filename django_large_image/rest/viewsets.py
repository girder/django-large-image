from functools import wraps
import pathlib
from typing import Union

from django.db.models.fields.files import FieldFile
from rest_framework.exceptions import APIException
from rest_framework.request import Request

from django_large_image import utilities
from django_large_image.rest.data import DataDetailMixin, DataMixin
from django_large_image.rest.metadata import MetaDataDetailMixin, MetaDataMixin
from django_large_image.rest.tiles import TilesDetailMixin, TilesMixin


class LargeImageMixin(DataMixin, MetaDataMixin, TilesMixin):
    """Mixin for large-image endpoints on a non-detail viewset.

    This is for use on a standalone ``ViewSet`` class with no detial views and
    not associated to a model. The ``detail`` attribute is set to ``False``
    for the django-rest-framework ``@action``.

    Subclasses must implement `get_path()`:

    .. code:: python

        def get_path(self, request: Request, pk: int = None):
            instance = Model.objects.get(pk=pk)
            return instance.file.name

    """

    pass


class LargeImageDetailMixin(DataDetailMixin, MetaDataDetailMixin, TilesDetailMixin):
    """Mixin class for large-image endpoints on detail viewset.

    Subclasses must implement `get_path()`:

    .. code:: python

        def get_path(self, request: Request, pk: int = None):
            instance = Model.objects.get(pk=pk)
            return instance.file.name

    """

    pass


class LargeImageFileDetailMixin(LargeImageDetailMixin):
    """Mixin specifically for detail viewsets that have a file field on the model.

    Define `FILE_FIELD_NAME` as the string name of the file field on the
    subclassed ViewSet's model.

    This mixin assumes `get_object()` is present - thus for ViewSets
    """

    FILE_FIELD_NAME: str = ''

    def get_field_file(self) -> FieldFile:
        """Get `FileField` using `FILE_FIELD_NAME`."""
        try:
            return getattr(self.get_object(), self.FILE_FIELD_NAME)  # type: ignore
        except (AttributeError, TypeError):
            # Raise 500 server error
            raise APIException('`FILE_FIELD_NAME` not properly set on viewset class.')

    @wraps(LargeImageDetailMixin.get_path)
    def get_path(self, request: Request, pk: int = None) -> Union[str, pathlib.Path]:
        return utilities.field_file_to_local_path(self.get_field_file())


class LargeImageVSIFileDetailMixin(LargeImageFileDetailMixin):
    USE_VSI: bool = True

    @wraps(LargeImageFileDetailMixin.get_path)
    def get_path(self, request: Request, pk: int = None) -> Union[str, pathlib.Path]:
        """Wrap get_path with VSI support."""
        field_file = self.get_field_file()
        if self.USE_VSI:
            with utilities.patch_internal_presign(field_file):
                # Grab URL and pass back VSI path
                # DO NOT return here to make sure this context is cleared
                vsi = utilities.make_vsi(field_file.url)
            return vsi
        # Checkout file locally if no VSI
        return LargeImageFileDetailMixin.get_path(self, request, pk)
