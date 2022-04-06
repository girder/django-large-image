from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageViewSetMixin, LargeImageVSIViewSetMixin
from django_large_image.utilities import make_vsi


class ImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageViewSetMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class VSIImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageViewSetMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3ImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageViewSetMixin,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3VSIImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageVSIViewSetMixin,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3URLLargeImageViewMixin(LargeImageViewSetMixin):
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
