from django_large_image import models, serializers
from rest_framework import mixins, viewsets


class ModelViewSet(
    # mixins.CreateModelMixin, 
    mixins.RetrieveModelMixin,
    # mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for read and edit models.

    Provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

    pass


class ImageSetViewSet(ModelViewSet):
    serializer_class = serializers.ImageSetSerializer
    queryset = models.ImageSet.objects.all()


class ImageViewSet(ModelViewSet):
    serializer_class = serializers.ImageSerializer
    queryset = models.Image.objects.all()

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary='Download the associated Image data for this Image directly from S3.',
    # )
    # @action(detail=True)
    # def data(self, *args, **kwargs):
    #     obj = self.get_object()
    #     url = obj.file.get_url()
    #     return HttpResponseRedirect(url)
