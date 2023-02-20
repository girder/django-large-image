from drf_spectacular.openapi import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from django_large_image.tilesource import get_formats

FORMAT_URL_PATTERN = rf'(?P<fmt>{r"|".join(get_formats())})'

projection = OpenApiParameter(
    'projection',
    location=OpenApiParameter.QUERY,
    description='The projection in which to open the image (try `EPSG:3857`).',
    type=OpenApiTypes.STR,
)
source = OpenApiParameter(
    'source',
    location=OpenApiParameter.QUERY,
    description='The source to use when opening the image. Use the `large-image/sources` endpoint to list the available sources.',
    type=OpenApiTypes.STR,
)

BASE = [projection, source]

fmt_png = OpenApiParameter(
    'fmt',
    location=OpenApiParameter.PATH,
    description=f'Image format ({" | ".join(get_formats())})',
    type=OpenApiTypes.STR,
    default='png',
)
fmt_tiff = OpenApiParameter(
    'fmt',
    location=OpenApiParameter.PATH,
    description=f'Image format ({" | ".join(get_formats())})',
    type=OpenApiTypes.STR,
    default='tiff',
)

z = OpenApiParameter(
    'z',
    location=OpenApiParameter.PATH,
    description='The Z level of the tile. May range from [0, levels], where 0 is the lowest resolution, single tile for the whole source.',
    type=OpenApiTypes.INT,
)
x = OpenApiParameter(
    'x',
    location=OpenApiParameter.PATH,
    description='The 0-based X position of the tile on the specified Z level.',
    type=OpenApiTypes.INT,
)
y = OpenApiParameter(
    'y',
    location=OpenApiParameter.PATH,
    description='The 0-based Y position of the tile on the specified Z level.',
    type=OpenApiTypes.INT,
)

# Style Parameters
palette = OpenApiParameter(
    'palette',
    location=OpenApiParameter.QUERY,
    description='The color palette to map the band values (named Matplotlib colormaps or palettable palettes). `cmap` alias supported.',
    type=OpenApiTypes.STR,
)
band = OpenApiParameter(
    'band',
    location=OpenApiParameter.QUERY,
    description='The band number to use.',
    type=OpenApiTypes.INT,
)
vmin = OpenApiParameter(
    'min',
    location=OpenApiParameter.QUERY,
    description='The minimum value for the color mapping.',
    type=OpenApiTypes.NUMBER,
)
vmax = OpenApiParameter(
    'max',
    location=OpenApiParameter.QUERY,
    description='The maximum value for the color mapping.',
    type=OpenApiTypes.NUMBER,
)
nodata = OpenApiParameter(
    'nodata',
    location=OpenApiParameter.QUERY,
    description='The value to map as no data (often made transparent).',
    type=OpenApiTypes.NUMBER,
)
scheme = OpenApiParameter(
    'scheme',
    location=OpenApiParameter.QUERY,
    description='This is either ``linear`` (the default) or ``discrete``. If a palette is specified, ``linear`` uses a piecewise linear interpolation, and ``discrete`` uses exact colors from the palette with the range of the data mapped into the specified number of colors (e.g., a palette with two colors will split exactly halfway between the min and max values).',
    type=OpenApiTypes.STR,
)
style = OpenApiParameter(
    'style',
    location=OpenApiParameter.QUERY,
    description='Encoded string of JSON style following https://girder.github.io/large_image/tilesource_options.html#style',
    type=OpenApiTypes.STR,
)

STYLE = [palette, band, vmin, vmax, nodata, scheme, style]

# Region Parameters
left = OpenApiParameter(
    'left',
    location=OpenApiParameter.QUERY,
    description='left',
    type=OpenApiTypes.NUMBER,
    required=True,
)
right = OpenApiParameter(
    'right',
    location=OpenApiParameter.QUERY,
    description='right',
    type=OpenApiTypes.NUMBER,
    required=True,
)
top = OpenApiParameter(
    'top',
    location=OpenApiParameter.QUERY,
    description='top',
    type=OpenApiTypes.NUMBER,
    required=True,
)
bottom = OpenApiParameter(
    'bottom',
    location=OpenApiParameter.QUERY,
    description='bottom',
    type=OpenApiTypes.NUMBER,
    required=True,
)
units = OpenApiParameter(
    'units',
    location=OpenApiParameter.QUERY,
    description='The projection/units of the region coordinates.',
    type=OpenApiTypes.STR,
)

REGION = [left, right, top, bottom, units, fmt_tiff]

# Histogram Parameters
only = OpenApiParameter(
    'onlyMinMax',
    location=OpenApiParameter.QUERY,
    type=OpenApiTypes.BOOL,
    default=False,
)
bins = OpenApiParameter(
    'bins',
    location=OpenApiParameter.QUERY,
    type=OpenApiTypes.INT,
    default=256,
)
density = OpenApiParameter(
    'density',
    location=OpenApiParameter.QUERY,
    type=OpenApiTypes.BOOL,
    default=False,
)
format = OpenApiParameter(
    'format',
    location=OpenApiParameter.QUERY,
    type=OpenApiTypes.STR,
)

HISTOGRAM = [only, bins, density, format]


# Thumbnail Parameters
max_width = OpenApiParameter(
    'max_width',
    location=OpenApiParameter.QUERY,
    description='maximum width in pixels.',
    type=OpenApiTypes.INT,
    default=256,
)
max_height = OpenApiParameter(
    'max_height',
    location=OpenApiParameter.QUERY,
    description='maximum height in pixels.',
    type=OpenApiTypes.INT,
    default=256,
)

THUMBNAIL = [fmt_png, max_height, max_width]
