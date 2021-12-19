from django.contrib import admin

from example.core.models import MyImageFile


@admin.register(MyImageFile)
class ImageSetAdmin(admin.ModelAdmin):
    list_display = ('pk', 'image',)
    raw_id_fields = ('image',)
    readonly_fields = ('image',)
