from django.contrib import admin

from myimages.imagefiles.models import ImageFile


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display_links = ('pk', 'name', 'thumbnail')
    list_display = ('pk', 'name', 'thumbnail', 'metadata', 'metadata_internal')
