from django.contrib import admin
from django_large_image.admin.mixins import MODIFIABLE_FILTERS
from django_large_image.models import Image, ImageSet


def make_image_set_from_images(modeladmin, request, queryset):
    imset = ImageSet()
    imset.save()  # Have to save before adding to ManyToManyField
    for image in queryset.all():
        imset.images.add(image)
    imset.save()
    return imset


def clean_empty_image_sets(modeladmin, request, queryset):
    """Delete empty `ImageSet`s."""
    q = queryset.filter(images=None)
    q.delete()


@admin.register(ImageSet)
class ImageSetAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'count',
        'modified',
        'created',
    )
    actions = (clean_empty_image_sets,)
    list_filter = MODIFIABLE_FILTERS
    raw_id_fields = ('images',)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'modified',
        'created',
    )
    readonly_fields = (
        'modified',
        'created',
    )
    actions = (make_image_set_from_images,)
    list_filter = MODIFIABLE_FILTERS
