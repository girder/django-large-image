from django.contrib import admin
from example.core.models import ImageFile, S3ImageFile


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('pk',)


@admin.register(S3ImageFile)
class S3ImageFileAdmin(admin.ModelAdmin):
    list_display = ('pk',)
