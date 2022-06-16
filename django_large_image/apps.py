import logging

from django.apps import AppConfig
from django.conf import settings
import large_image

from django_large_image.cache import DjangoCache

logger = logging.getLogger(__name__)


class DjangoLargeImageConfig(AppConfig):
    name = 'django_large_image'
    verbose_name = 'Django Large Image'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Set up cache with large_image
        # This isn't necessary but it makes sure we always default
        #   to the django cache if others are available
        large_image.config.setConfig('cache_backend', 'django')
