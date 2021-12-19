from django_large_image.models import LargeImageFile
from django_large_image.utilities import get_cache_dir
from s3_file_field import S3FileField

from ..utilities import field_file_to_local_path


class MyImageFile(LargeImageFile):
    file = S3FileField()

    def get_image_local_path(self):
        name = '-'.join(self.file.name.split('/'))
        path = get_cache_dir() / f'{self.pk}-{name}'
        return field_file_to_local_path(self.file, path)
