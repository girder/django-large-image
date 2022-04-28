import logging

from django.apps import AppConfig
from django.conf import settings


class MyImagesConfig(AppConfig):
    name = 'myimages.imagefiles'
    verbose_name = 'My Image Files'

    def ready(self):
        if not getattr(settings, 'DEBUG', False):
            logging.getLogger('gdal').setLevel(logging.ERROR)
            logging.getLogger('large_image').setLevel(logging.ERROR)
            logging.getLogger('tifftools').setLevel(logging.ERROR)
            logging.getLogger('pyvips').setLevel(logging.ERROR)
            logging.getLogger('PIL').setLevel(logging.ERROR)
