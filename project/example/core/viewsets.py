from django.contrib.auth.mixins import LoginRequiredMixin
from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageView


class ImageFileDetailView(
    LoginRequiredMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageView,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'
    USE_VSI = True


class S3ImageFileDetailView(
    LoginRequiredMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageView,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'
    USE_VSI = True
