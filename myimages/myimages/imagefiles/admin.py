from django.contrib import admin

from myimages.imagefiles.models import ImageFile


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display_links = ('pk', 'thumbnail', 'name')
    list_display = ('pk', 'thumbnail', 'name', 'metadata', 'metadata_internal')
