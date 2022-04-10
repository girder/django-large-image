from example.core import models
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError

from django_large_image.rest.viewsets import (
    LargeImageDetailMixin,
    LargeImageFileDetailMixin,
    LargeImageMixin,
    LargeImageVSIFileDetailMixin,
)
from django_large_image.utilities import make_vsi


class ImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageFileDetailMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class VSIImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageVSIFileDetailMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3ImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageFileDetailMixin,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3VSIImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageVSIFileDetailMixin,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3URLLargeImageViewMixin(LargeImageDetailMixin):
    def get_path(self, request, pk):
        object = self.get_object()
        return make_vsi(object.url)


class URLImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    S3URLLargeImageViewMixin,
):
    queryset = models.URLImageFile.objects.all()
    serializer_class = models.URLImageFileSerializer


class URLLargeImageViewSet(viewsets.ViewSet, LargeImageMixin):
    def get_path(self, request, pk=None):
        try:
            url = request.query_params.get('url')
            if not url:
                raise KeyError
        except KeyError:
            raise ValidationError('url must be defined as a query parameter.')
        return make_vsi(url)
