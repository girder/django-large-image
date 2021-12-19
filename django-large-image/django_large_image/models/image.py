"""Base classes for raster dataset entries."""
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_extensions.db.models import TimeStampedModel


class LargeImageField(models.OneToOneField):
    def __init__(self, **kwargs):
        kwargs['to'] = 'django_large_image.image'
        kwargs['related_name'] = 'large_image_file_source_%(app_label)s_%(class)s'
        kwargs['on_delete'] = models.CASCADE
        super().__init__(**kwargs)


class Image(TimeStampedModel):
    """This is a standalone DB entry for image files.

    This is not intended to be used directly in relationships downstream.
    Please use the ``LargeImageFile`` interface.

    """

    def get_image_local_path(self):
        related = [name for name in dir(self) if name.startswith('large_image_file_source_')]
        if not related:
            raise Exception('No related file source models')
        for name in related:
            try:
                obj = getattr(self, name)
                if obj:
                    if not hasattr(obj, 'get_image_local_path'):
                        raise Exception('Related model does not implement `get_image_local_path`')
                    return obj.get_image_local_path()
            except ObjectDoesNotExist:
                pass
        raise Exception('No related model records for this Image entry')


class ImageSet(TimeStampedModel):
    """Container for many images."""

    name = models.CharField(max_length=1000, blank=True)
    description = models.TextField(null=True, blank=True)

    images = models.ManyToManyField(Image)

    @property
    def count(self):
        return self.images.count()


class LargeImageFile(models.Model):
    """Interface for using the Image model with custom file management."""

    class Meta:
        abstract = True

    image = LargeImageField()

    def get_image_local_path(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if not self.pk:
            self.image = Image.objects.create()
        super().save(*args, **kwargs)
