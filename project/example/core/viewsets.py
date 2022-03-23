from example.core import models
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from django_large_image.rest import LargeImageView


class ImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageView,
):
    permission_classes = [IsAuthenticated]
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'
    USE_VSI = True


class S3ImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageView,
):
    permission_classes = [IsAuthenticated]
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'
    USE_VSI = True
