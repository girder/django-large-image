import io
import json
import pathlib

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import tilesource
from django_large_image.rest import params
from django_large_image.rest.base import LargeImageMixinBase
from django_large_image.serializers.metadata import (
    BandSerializer,
    BandsSerializer,
    FramesSerializer,
    MetaDataInternalSerializer,
    MetaDataSerializer,
    TiffdumpSerializer,
)

try:
    import tifftools
    from tifftools.exceptions import TifftoolsError
except ImportError:  # pragma: no cover
    tifftools = None
    TifftoolsError = None

metadata_summary = 'Returns tile metadata.'
metadata_parameters = params.BASE
metadata_responses = {200: MetaDataSerializer}
metadata_internal_summary = 'Returns additional known metadata about the tile source.'
metadata_internal_parameters = params.BASE
metadata_internal_responses = {200: MetaDataInternalSerializer}
bands_summary = 'Returns bands information.'
bands_parameters = params.BASE
bands_responses = {200: BandsSerializer}
band_summary = 'Returns single band information.'
band_parameters = params.BASE + [params.band]
band_responses = {200: BandSerializer}
frames_summary = 'Retrieve all channels/bands for each frame. This is used to generate a UI to control how the image is displayed.'
frames_parameters = params.BASE
frames_responses = {200: FramesSerializer}
tiffdump_summary = 'Returns tifftools tiffdump JSON. This will raise a `ValidationError` if the image is not a Tiff.'
tiffdump_responses = {200: TiffdumpSerializer}


class MetaDataMixin(LargeImageMixinBase):
    @swagger_auto_schema(
        method='GET',
        operation_summary=metadata_summary,
        manual_parameters=metadata_parameters,
        responses=metadata_responses,
    )
    @action(detail=False, url_path='info/metadata')
    def metadata(self, request: Request, pk: int = None) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = tilesource.get_metadata(source)
        return Response(metadata)
        # return Response(MetaDataSerializer(metadata).data)

    @swagger_auto_schema(
        method='GET',
        operation_summary=metadata_internal_summary,
        manual_parameters=metadata_internal_parameters,
        responses=metadata_internal_responses,
    )
    @action(detail=False, url_path='info/metadata_internal')
    def metadata_internal(self, request: Request, pk: int = None) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = tilesource.get_metadata_internal(source)
        return Response(metadata)
        # return Response(MetaDataInternalSerializer(metadata).data)

    @swagger_auto_schema(
        method='GET',
        operation_summary=bands_summary,
        manual_parameters=bands_parameters,
        responses=bands_responses,
    )
    @action(detail=False, url_path='info/bands')
    def bands(self, request: Request, pk: int = None) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        bands = source.getBandInformation()
        return Response(BandsSerializer({'bands': bands}).data)

    @swagger_auto_schema(
        method='GET',
        operation_summary=bands_summary,
        manual_parameters=band_parameters,
        responses=band_responses,
    )
    @action(detail=False, url_path='info/band')
    def band(self, request: Request, pk: int = None) -> Response:
        # TODO: handle frame choice
        band = int(self.get_query_param(request, 'band', 1))
        source = self.get_tile_source(request, pk, style=False)
        metadata = source.getOneBandInformation(band)
        return Response(BandSerializer(metadata).data)

    @swagger_auto_schema(
        method='GET',
        operation_summary=frames_summary,
        manual_parameters=frames_parameters,
        responses=frames_responses,
    )
    @action(detail=False, url_path='info/frames')
    def frames(self, request: Request, pk: int = None) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        data = tilesource.get_frames(source)
        return Response(data)
        # return Response(FramesSerializer(data).data)

    @swagger_auto_schema(
        method='GET',
        operation_summary=tiffdump_summary,
        responses=tiffdump_responses,
    )
    @action(detail=False, url_path='info/tiffdump')
    def tiffdump(self, request: Request, pk: int = None) -> Response:
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
        # return Response(TiffdumpSerializer(...).data)


class MetaDataDetailMixin(MetaDataMixin):
    @swagger_auto_schema(
        method='GET',
        operation_summary=metadata_summary,
        manual_parameters=metadata_parameters,
        responses=metadata_responses,
    )
    @action(detail=True, url_path='info/metadata')
    def metadata(self, request: Request, pk: int = None) -> Response:
        return super().metadata(request, pk)

    @swagger_auto_schema(
        method='GET',
        operation_summary=metadata_internal_summary,
        manual_parameters=metadata_internal_parameters,
        responses=metadata_internal_responses,
    )
    @action(detail=True, url_path='info/metadata_internal')
    def metadata_internal(self, request: Request, pk: int = None) -> Response:
        return super().metadata_internal(request, pk)

    @swagger_auto_schema(
        method='GET',
        operation_summary=bands_summary,
        manual_parameters=bands_parameters,
        responses=bands_responses,
    )
    @action(detail=True, url_path='info/bands')
    def bands(self, request: Request, pk: int = None) -> Response:
        return super().bands(request, pk)

    @swagger_auto_schema(
        method='GET',
        operation_summary=bands_summary,
        manual_parameters=band_parameters,
        responses=band_responses,
    )
    @action(detail=True, url_path='info/band')
    def band(self, request: Request, pk: int = None) -> Response:
        return super().band(request, pk)

    @swagger_auto_schema(
        method='GET',
        operation_summary=frames_summary,
        manual_parameters=frames_parameters,
        responses=frames_responses,
    )
    @action(detail=True, url_path='info/frames')
    def frames(self, request: Request, pk: int = None) -> Response:
        return super().frames(request, pk)

    @swagger_auto_schema(
        method='GET',
        operation_summary=tiffdump_summary,
        responses=tiffdump_responses,
    )
    @action(detail=True, url_path='info/tiffdump')
    def tiffdump(self, request: Request, pk: int = None) -> Response:
        return super().tiffdump(request, pk)
