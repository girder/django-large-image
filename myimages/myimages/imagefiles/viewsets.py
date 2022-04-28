from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageFileDetailMixin
from myimages.imagefiles import models


class ImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageFileDetailMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer

    # for `django-large-image`: the name of the image FileField on your model
    FILE_FIELD_NAME = 'file'
