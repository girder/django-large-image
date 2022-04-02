from django.contrib import admin
from example.core.models import ImageFile, S3ImageFile, URLImageFile


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display_links = ('pk', 'thumbnail')
    list_display = ('pk', 'thumbnail', 'metadata', 'internal_metadata')


@admin.register(S3ImageFile)
class S3ImageFileAdmin(admin.ModelAdmin):
    list_display_links = ('pk', 'thumbnail')
    list_display = ('pk', 'thumbnail', 'metadata', 'internal_metadata')


@admin.register(URLImageFile)
class URLImageFileAdmin(admin.ModelAdmin):
    list_display_links = ('pk', 'thumbnail')
    list_display = ('pk', 'thumbnail', 'metadata', 'internal_metadata')
