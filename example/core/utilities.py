import os
import pathlib
import shutil

from django.core.files import File
from django.db.models.fields.files import FieldFile


def field_file_to_local_path(field_file: FieldFile, path: str) -> pathlib.Path:
    """Download entire FieldFile to disk location.

    This overrides `girder_utils.field_file_to_local_path` to download file to
    local path without a context manager. Cleanup must be handled by caller.

    """
    dest_path = pathlib.Path(path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    the_path = pathlib.Path(dest_path)
    with field_file.open('rb'):
        file_obj: File = field_file.file
        if type(file_obj) is File:
            # When file_obj is an actual File, (typically backed by FileSystemStorage),
            # it is already at a stable path on disk.
            # We must symlink it into the desired path
            os.symlink(file_obj.name, dest_path)
            return the_path
        else:
            # When file_obj is actually a subclass of File, it only provides a Python
            # file-like object API. So, it must be copied to a stable path.
            if dest_path.exists():
                # WARNING: this is probably not thread safe
                #  S3FF is fundamentally incompatible with tile serving
                return dest_path
            with open(dest_path, 'wb') as dest_stream:
                shutil.copyfileobj(file_obj, dest_stream)
                dest_stream.flush()
            return the_path
