import logging

from django.apps import AppConfig
from django.conf import settings
import large_image

logger = logging.getLogger(__name__)


class DjangoLargeImageConfig(AppConfig):
    name = 'django_large_image'
    verbose_name = 'Django Large Image'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Set up cache with large_image
        # Use any existing settings defined by other installed apps,
        # Defaulting to caching with django
        large_image.config.setConfig(
            'cache_backend',
            getattr(settings, 'LARGE_IMAGE_CACHE_BACKEND', 'django'),
        )

        # Set any other cache config if settings are defined
        for config_var_name in [
            'cache_python_memory_portion',
            'cache_memcached_url',
            'cache_memcached_username',
            'cache_memcached_password',
            'cache_redis_url',
            'cache_redis_username',
            'cache_redis_password',
            'cache_tilesource_memory_portion',
            'cache_tilesource_maximum',
            'cache_sources',
        ]:
            settings_attr_name = 'LARGE_IMAGE_' + config_var_name.upper()
            settings_attr_value = getattr(settings, settings_attr_name, None)
            if settings_attr_value is not None:
                large_image.config.setConfig(config_var_name, settings_attr_value)
