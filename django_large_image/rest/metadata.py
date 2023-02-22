import io
import json
import pathlib

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import tilesource
from django_large_image.rest import params
from django_large_image.rest.base import LargeImageMixinBase

try:
    import tifftools
    from tifftools.exceptions import TifftoolsError
except ImportError:  # pragma: no cover
    tifftools = None
    TifftoolsError = None

metadata_summary = 'Returns tile metadata.'
metadata_parameters = params.BASE
metadata_internal_summary = 'Returns additional known metadata about the tile source.'
metadata_internal_parameters = params.BASE
bands_summary = 'Returns bands information.'
bands_parameters = params.BASE
band_summary = 'Returns single band information.'
band_parameters = params.BASE + [params.band]
frames_summary = 'Retrieve all channels/bands for each frame. This is used to generate a UI to control how the image is displayed.'
frames_parameters = params.BASE
tiffdump_summary = 'Returns tifftools tiffdump JSON. This will raise a `ValidationError` if the image is not a Tiff.'


class MetaDataMixin(LargeImageMixinBase):
    @extend_schema(
        methods=['GET'],
        summary=metadata_summary,
        parameters=metadata_parameters,
    )
    @action(detail=False, url_path='info/metadata')
    def metadata(self, request: Request, pk: int = None, **kwargs) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = tilesource.get_metadata(source)
        return Response(metadata)

    @extend_schema(
        methods=['GET'],
        summary=metadata_internal_summary,
        parameters=metadata_internal_parameters,
    )
    @action(detail=False, url_path='info/metadata_internal')
    def metadata_internal(self, request: Request, pk: int = None, **kwargs) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = tilesource.get_metadata_internal(source)
        return Response(metadata)

    @extend_schema(
        methods=['GET'],
        summary=bands_summary,
        parameters=bands_parameters,
    )
    @action(detail=False, url_path='info/bands')
    def bands(self, request: Request, pk: int = None, **kwargs) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = source.getBandInformation()
        return Response(metadata)

    @extend_schema(
        methods=['GET'],
        summary=bands_summary,
        parameters=band_parameters,
    )
    @action(detail=False, url_path='info/band')
    def band(self, request: Request, pk: int = None, **kwargs) -> Response:
        # TODO: handle frame choice
        band = int(self.get_query_param(request, 'band', 1))
        source = self.get_tile_source(request, pk, style=False)
        metadata = source.getOneBandInformation(band)
        return Response(metadata)

    @extend_schema(
        methods=['GET'],
        summary=frames_summary,
        parameters=frames_parameters,
    )
    @action(detail=False, url_path='info/frames')
    def frames(self, request: Request, pk: int = None, **kwargs) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        data = tilesource.get_frames(source)
        return Response(data)

    @extend_schema(
        methods=['GET'],
        summary=tiffdump_summary,
    )
    @action(detail=False, url_path='info/tiffdump')
    def tiffdump(self, request: Request, pk: int = None, **kwargs) -> Response:
        if tifftools is None:  # pragma: no cover
            raise APIException('`tifftools` is not installed on the server.')
        source = self.get_tile_source(request, pk, style=False)
        # This will only work for local files (path on disk)
        path = source._getLargeImagePath()
        try:
            if not pathlib.Path(path).exists():
                raise OSError  # pragma: no cover
        except OSError:
            raise APIException(
                'The image path is not local and tifftools will not be able to open this image.'
            )
        output = io.StringIO()
        try:
            tifftools.tiff_dump(path, dest=output, outformat='json')
        except (TifftoolsError, OSError) as e:
            raise ValidationError(str(e))
        output.seek(0)
        return Response(json.loads(output.read()))


class MetaDataDetailMixin(MetaDataMixin):
    @extend_schema(
        methods=['GET'],
        summary=metadata_summary,
        parameters=metadata_parameters,
    )
    @action(detail=True, url_path='info/metadata')
    def metadata(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().metadata(request, pk)

    @extend_schema(
        methods=['GET'],
        summary=metadata_internal_summary,
        parameters=metadata_internal_parameters,
    )
    @action(detail=True, url_path='info/metadata_internal')
    def metadata_internal(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().metadata_internal(request, pk)

    @extend_schema(
        methods=['GET'],
        summary=bands_summary,
        parameters=bands_parameters,
    )
    @action(detail=True, url_path='info/bands')
    def bands(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().bands(request, pk)

    @extend_schema(
        methods=['GET'],
        summary=bands_summary,
        parameters=band_parameters,
    )
    @action(detail=True, url_path='info/band')
    def band(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().band(request, pk)

    @extend_schema(
        methods=['GET'],
        summary=frames_summary,
        parameters=frames_parameters,
    )
    @action(detail=True, url_path='info/frames')
    def frames(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().frames(request, pk)

    @extend_schema(
        methods=['GET'],
        summary=tiffdump_summary,
    )
    @action(detail=True, url_path='info/tiffdump')
    def tiffdump(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().tiffdump(request, pk)
