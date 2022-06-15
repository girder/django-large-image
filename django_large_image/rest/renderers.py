from rest_framework.renderers import BaseRenderer as RFBaseRenderer


class BaseRenderer(RFBaseRenderer):
    render_style = 'binary'
    charset = None

    def render(self, data, media_type=None, renderer_context=None):
        return data


class PNGRenderer(BaseRenderer):
    media_type = 'image/png'
    format = 'png'


class JPEGRenderer(BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpeg'


class JPGRenderer(BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'


image_renderers = [PNGRenderer, JPEGRenderer, JPGRenderer]


class TifRenderer(BaseRenderer):
    media_type = 'image/tiff'
    format = 'tif'


class TiffRenderer(BaseRenderer):
    media_type = 'image/tiff'
    format = 'tiff'


image_data_renderers = image_renderers + [TifRenderer, TiffRenderer]
