from django_large_image import models, serializers
from rest_framework import mixins, viewsets


class ModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for read and edit models.

    Provides default `retrieve()` and `list()` actions.
    """

    pass


class ImageSetViewSet(ModelViewSet):
    serializer_class = serializers.ImageSetSerializer
    queryset = models.ImageSet.objects.all()


class ImageViewSet(ModelViewSet):
    serializer_class = serializers.ImageSerializer
    queryset = models.Image.objects.all()
