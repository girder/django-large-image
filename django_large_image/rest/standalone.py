import logging

import large_image
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class ListTileSourcesView(APIView):
    def get(self, request: Request) -> Response:
        large_image.tilesource.loadTileSources()
        sources = large_image.tilesource.AvailableTileSources
        return Response({k: str(v) for k, v in sources.items()})


class ListColormapsView(APIView):
    def get(self, request: Request) -> Response:
        """List of available palettes.

        This does not currently list the palettable palettes there isn't a clean
        way to list all of them.
        """
        simple = {
            'red': ['#000', '#f00'],
            'r': ['#000', '#f00'],
            'green': ['#000', '#0f0'],
            'g': ['#000', '#0f0'],
            'blue': ['#000', '#00f'],
            'b': ['#000', '#00f'],
        }
        cmaps = {}
        try:
            import matplotlib.pyplot

            cmaps['matplotlib'] = list(matplotlib.pyplot.colormaps())
        except ImportError:  # pragma: no cover
            logger.error('Install matplotlib for additional colormap choices.')
        cmaps['simple'] = [s for s in simple.keys() if len(s) > 1]
        return Response(cmaps)
