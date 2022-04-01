from django.db import models
from django.utils.html import mark_safe
from django_extensions.db.models import TimeStampedModel
from rest_framework import serializers
from rest_framework.reverse import reverse
from s3_file_field import S3FileField


def thumbnail_html(url):
    return mark_safe(f'<img src="{url}" style="height:100px;"/>')


class ImageFile(TimeStampedModel):
    file = models.FileField()

    def thumbnail(self):
        return thumbnail_html(reverse('image-file-thumbnail', args=[self.pk]))

    thumbnail.allow_tags = True


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = '__all__'


class S3ImageFile(TimeStampedModel):
    file = S3FileField()

    def thumbnail(self):
        return thumbnail_html(reverse('s3-image-file-thumbnail', args=[self.pk]))

    thumbnail.allow_tags = True


class S3ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3ImageFile
        fields = '__all__'
