from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageViewMixin, LargeImageVSIViewMixin
from django_large_image.utilities import make_vsi


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


class S3URLLargeImageViewMixin(LargeImageViewMixin):
    def get_path(self, request, pk):
        object = self.get_object()
        return make_vsi(object.url)


class URLImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    S3URLLargeImageViewMixin,
):
    queryset = models.URLImageFile.objects.all()
    serializer_class = models.URLImageFileSerializer
