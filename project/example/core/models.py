from django.db import models
from django.utils.html import mark_safe
from django_extensions.db.models import TimeStampedModel
from rest_framework import serializers
from rest_framework.reverse import reverse
from s3_file_field import S3FileField


def thumbnail_html(url):
    return mark_safe(f'<img src="{url}" style="height:100px;"/>')


def a_html(url, label):
    return mark_safe(f'<a href="{url}" target="_blank">{label}</a>')


class Mixin:
    def thumbnail(self):
        return thumbnail_html(reverse(f'{self.url_name}-thumbnail', args=[self.pk]))

    thumbnail.allow_tags = True

    def metadata(self):
        return a_html(reverse(f'{self.url_name}-metadata', args=[self.pk]), 'metadata')

    metadata.allow_tags = True

    def internal_metadata(self):
        return a_html(
            reverse(f'{self.url_name}-internal-metadata', args=[self.pk]), 'internal metadata'
        )

    internal_metadata.allow_tags = True


class ImageFile(TimeStampedModel, Mixin):
    file = models.FileField()

    url_name = 'image-file'


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = '__all__'


class S3ImageFile(TimeStampedModel, Mixin):
    file = S3FileField()

    url_name = 's3-image-file'


class S3ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3ImageFile
        fields = '__all__'


class URLImageFile(models.Model, Mixin):
    name = models.TextField()
    url = models.TextField()

    url_name = 'url-image-file'


class URLImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLImageFile
        fields = '__all__'
