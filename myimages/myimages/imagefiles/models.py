from django.db import models
from rest_framework import serializers


class ImageFile(models.Model):
    name = models.TextField(null=True, blank=True)
    file = models.FileField()


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = '__all__'
