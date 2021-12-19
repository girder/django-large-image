from django_large_image import models
from django_large_image.serializers.mixins import MODIFIABLE_READ_ONLY_FIELDS, RelatedField
from rest_framework import serializers


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = '__all__'
        read_only_fields = MODIFIABLE_READ_ONLY_FIELDS


class ImageSetSerializer(serializers.ModelSerializer):
    images = RelatedField(
        queryset=models.Image.objects.all(), serializer=ImageSerializer, many=True
    )

    class Meta:
        model = models.ImageSet
        fields = '__all__'
        read_only_fields = MODIFIABLE_READ_ONLY_FIELDS
