import os

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django_large_image import models


@receiver(m2m_changed, sender=models.ImageSet.images.through)
def _m2m_changed_image_set(sender, instance, action, reverse, *args, **kwargs):
    # If no name was specified for an ImageSet, when images are added to it,
    # use the common base name of all images as the name of the ImageSet.
    if action == 'post_add' and not instance.name and instance.images.count():
        names = [image.file.name for image in instance.images.all() if image.file.name]
        if len(names):
            instance.name = os.path.commonprefix(names)
            instance.save(update_fields=['name'])
