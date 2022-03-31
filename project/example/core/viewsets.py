from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageViewMixin, LargeImageVSIViewMixin


class ImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageViewMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class VSIImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageVSIViewMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3ImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageViewMixin,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3VSIImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageVSIViewMixin,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'
