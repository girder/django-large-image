from django.contrib.auth.mixins import LoginRequiredMixin
from django_large_image.rest import LargeImageView
from rest_framework import mixins, viewsets

from example.core import models


class ImageFileDetailView(
    LoginRequiredMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageView,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer
    FILE_FIELD_NAME = 'file'


class S3ImageFileDetailView(
    LoginRequiredMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageView,
):
    queryset = models.S3ImageFile.objects.all()
    serializer_class = models.S3ImageFileSerializer
    FILE_FIELD_NAME = 'file'
