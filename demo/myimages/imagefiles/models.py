from django.db import models
from django.utils.html import mark_safe
from rest_framework import serializers
from rest_framework.reverse import reverse


def thumbnail_html(url):
    return mark_safe(f'<img src="{url}" style="height:100px;"/>')


def a_html(url, label):
    return mark_safe(f'<a href="{url}" target="_blank">{label}</a>')


class Mixin:
    def thumbnail(self):
        return thumbnail_html(reverse('imagefile-thumbnail-png', args=[self.pk]))

    thumbnail.allow_tags = True  # type: ignore

    def metadata(self):
        return a_html(reverse('imagefile-metadata', args=[self.pk]), 'metadata')

    metadata.allow_tags = True  # type: ignore

    def metadata_internal(self):
        return a_html(reverse('imagefile-metadata-internal', args=[self.pk]), 'internal metadata')

    metadata_internal.allow_tags = True  # type: ignore


class ImageFile(models.Model, Mixin):
    name = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='data/')


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = '__all__'
