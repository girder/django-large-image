import logging

from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = 'example.core'
    verbose_name = 'Django Large Image: Core'

    def ready(self):
        if not getattr(settings, 'DEBUG', False):
            logging.getLogger("gdal").setLevel(logging.ERROR)
            logging.getLogger("large_image").setLevel(logging.ERROR)
            logging.getLogger("tifftools").setLevel(logging.ERROR)
            logging.getLogger("pyvips").setLevel(logging.ERROR)
            logging.getLogger("PIL").setLevel(logging.ERROR)
