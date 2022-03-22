from django.db import models
from django_extensions.db.models import TimeStampedModel
from rest_framework import serializers
from s3_file_field import S3FileField


class ImageFile(TimeStampedModel):
    file = models.FileField()


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = '__all__'


class S3ImageFile(TimeStampedModel):
    file = S3FileField()


class S3ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3ImageFile
        fields = '__all__'
