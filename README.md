# 🩻 🗺️ django-large-image


<p align="center">
  <img src="https://raw.githubusercontent.com/girder/django-large-image/main/doc/admin.png"/>
  <p align="center">Dynamic tile server in Django built  on top of large-image (and GDAL)</p>
</p>

<p align="center">
  <a href="https://www.kitware.com/" target="_blank">
      <img src="https://img.shields.io/badge/Made%20by-Kitware-blue" alt="Made by Kitware">
  </a>
  <a href="https://pypi.org/project/django-large-image/" target="_blank">
      <img src="https://img.shields.io/pypi/v/django-large-image.svg?logo=python&logoColor=white" alt="PyPI">
  </a>
  <a href="https://anaconda.org/conda-forge/django-large-image" target="_blank">
      <img src="https://img.shields.io/conda/vn/conda-forge/django-large-image.svg?logo=conda-forge&logoColor=white" alt="conda-forge">
  </a>
  <a href="https://codecov.io/gh/girder/django-large-image" target="_blank">
      <img src="https://codecov.io/gh/girder/django-large-image/branch/main/graph/badge.svg?token=VBK1F6JWNY" alt="codecov">
  </a>
  <a href="https://github.com/girder/django-large-image/actions/workflows/ci.yml" target="_blank">
      <img src="https://github.com/girder/django-large-image/actions/workflows/ci.yml/badge.svg" alt="Tests">
  </a>
</p>


`django-large-image` is an abstraction of [`large-image`](https://github.com/girder/large_image)
for use with `django-rest-framework` providing viewset mixins for endpoints to
work with large images (Cloud Optimized GeoTiffs or medical image formats) in
Django. The dynamic tile server provided here prevents the need for
preprocessing large images into tile sets for viewing interactively on
slippy-maps. Under the hood, large-image applies operations (rescaling,
reprojection, image encoding) to create image tiles on-the-fly.

| Lightning Talk for 2022 Cloud-Native Geospatial Outreach Event |
|-|
| [![outreach event video](https://raw.githubusercontent.com/girder/django-large-image/main/doc/outreach_video.png)](https://youtu.be/v3e2ODCK9Co?t=31247) |
| [View slides here](https://docs.google.com/presentation/d/1T_bmtxx1qR8GgzXdFer3LwDi_dxp6X4RqndbsSVhWTg/edit?usp=sharing) |


## ℹ️ Overview

This package brings Kitware's [large-image](https://github.com/girder/large_image)
to Django by providing a set of abstract, mixin API viewset classes that will
handle tile serving, fetching metadata from images, and extracting regions of
interest.

`django-large-image` is an installable Django app with
a few classes that can be mixed into a Django project (or application)'s
drf-based viewsets to provide tile serving endpoints out of the box. Notably,
`django-large-image` is designed to work specifically with `FileField`
interfaces with development being tailored to Kitware's
[`S3FileField`](https://github.com/girder/django-s3-file-field). GeoDjango's [`GDALRaster`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster)
can also be used by returning `GDALRaster.name` in the `get_path()` override.

This package ships with pre-made HTML templates for rendering geospatial image
tiles with CesiumJS and non-geospatial image tiles with [GeoJS](https://github.com/OpenGeoscience/geojs).

### 🤝 Support [![Kitware](https://img.shields.io/badge/Made%20by-Kitware-blue)](https://www.kitware.com/)

`django-large-image` and the supporting [`large-image`](https://github.com/girder/large_image)
library are developed and  maintained by the Data & Analytics group at
[Kitware, Inc.](https://www.kitware.com/)
We work with large image data in both the geospatial and medical capacities.
If you have questions about these technologies, or you would like to discuss
your own geospatial and medical image problems and learn how we can help,
please reach out at kitware@kitware.com. We look forward to the conversation!

### 🌟 Features

Rich set of RESTful endpoints to extract information from large image formats:
- Image metadata (`/info/metadata`, `/info/metadata_internal`)
- Tile serving (`/tiles/{z}/{x}/{y}.png?projection=EPSG:3857`)
- Region extraction (`/data/region.tif?left=v&right=v&top=v&bottom=v`)
- Image thumbnails (`/data/thumbnail.png`)
- Individual pixels (`/data/pixel?left=v&top=v`)
- Band histograms (`/data/histogram`)

Support for any storage backend:
- Supports Django's `FileField`
- Supports [`S3FileField`](https://github.com/girder/django-s3-file-field)
- Customizable method for handling data access (`get_path` override)
- Supports GDAL's [Virtual File System](https://gdal.org/user/virtual_file_systems.html) for `s3://`, `ftp://`, etc. URLs

Miscellaneous:
- Admin interface widget for viewing image tiles.
- Caching - tile sources are cached for rapid file re-opening
  - tiles and thumbnails are cached to prevent recreating these data on multiple requests
- Easily extensible SSR templates for tile viewing with CesiumJS and GeoJS
- OpenAPI specification

| OpenAPI Documentation | Tiles Endpoint |
|---|---|
|![swagger-spec](https://raw.githubusercontent.com/girder/django-large-image/main/doc/swagger.png) | ![tiles-spec](https://raw.githubusercontent.com/girder/django-large-image/main/doc/tiles_endpoint.png)|

## ⬇️ Installation

Out of the box, `django-large-image` only depends of the core `large-image`
module, but you will need a `large-image-source-*` module in order for this
to work. Most of our users probably want to work with geospatial images so we
will focus on the `large-image-source-gdal` case, but it is worth noting that
`large-image` has source modules for a wide variety of image formats
(e.g., medical image formats for microscopy).

See [`large-image`](https://github.com/girder/large_image#installation)'s
installation instructions for more details.

**Tip:* installing GDAL is notoriously difficult, so at Kitware we provide
pre-built Python wheels with the GDAL binary bundled for easily installation in
production environments. To install our GDAL wheel, use:
`pip install --find-links https://girder.github.io/large_image_wheels GDAL`*


```bash
pip install \
  --find-links https://girder.github.io/large_image_wheels \
  django-large-image \
  'large-image[gdal,pil]>=1.14'
```

### 🐍 Conda

```bash
conda install -c conda-forge django-large-image large-image-source-gdal
```


## 🚀 Usage

Simply install the app and mixin one of the mixing classes to your
existing `django-rest-framework` viewset.

```py
# settings.py
INSTALLED_APPS = [
    ...,
    'django_large_image',
]
```

The following are the provided mixin classes and their use case:

- `LargeImageMixin`: for use with a standard, non-detail `ViewSet`. Users must implement `get_path()`
- `LargeImageDetailMixin`: for use with a detail viewset like `GenericViewSet`. Users must implement `get_path()`
- `LargeImageFileDetailMixin`: (most commonly used) for use with a detail viewset like `GenericViewSet` where the associated model has a `FileField` storing the image data.
- `LargeImageVSIFileDetailMixin`: (geospatial) for use with a detail viewset like `GenericViewSet` where the associated model has a `FileField` storing the image data that is intended to be read with GDAL. This will access the data over GDAL's Virtual File System interface (a VSI path).

Most users will want to use `LargeImageFileDetailMixin` and so the following
example demonstrate how to use it:

Specify the `FILE_FIELD_NAME` as the string name of the `FileField` in which
your image data are saved on the associated model.

```py
# viewsets.py
from rest_framework import viewsets
from django_large_image.rest import LargeImageFileDetailMixin

class MyModelViewSet(viewsets.GenericViewSet, LargeImageFileDetailMixin):
  ...  # configuration for your model's viewset
  FILE_FIELD_NAME = 'field_name'
```

```py
# urls.py
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from myapp.viewsets import MyModelViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'api/my-model', MyModelViewSet)

urlpatterns = [
  # Additional, standalone URLs from django-large-image
  path('', include('django_large_image.urls')),
] + router.urls
```

And that's it!

### 📝 Example Code

To use the mixin classes provided here, create a model, serializer, and viewset
in your Django project like so:

```py
# models.py
from django.db import models
from rest_framework import serializers


class ImageFile(models.Model):
    name = models.TextField()
    file = models.FileField()


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = '__all__'
```

```py
# admin.py
from django.contrib import admin
from example.core.models import ImageFile


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')
```

Then create the viewset, mixing in the `django-large-image` viewset class:
```py
# viewsets.py
from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageFileDetailMixin


class ImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageFileDetailMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer

    # for `django-large-image`: the name of the image FileField on your model
    FILE_FIELD_NAME = 'file'
```

Then register the URLs:

```py
# urls.py
from django.urls import include, path
from example.core.viewsets import ImageFileDetailViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/image-file', ImageFileDetailViewSet)

urlpatterns = [
  # Additional, standalone URLs from django-large-image
  path('', include('django_large_image.urls')),
] + router.urls
```

You can also use an admin widget for your model:

```html
<!-- templates/admin/myapp/imagefile/change_form.html -->
{% extends "admin/change_form.html" %}

{% block after_field_sets %}

<script>
  var baseEndpoint = 'api/image-file';
</script>

{% include 'admin/django_large_image/_include/geojs.html' %}

{% endblock %}
```

Please note the example Django project in the `project/` directory of this
repository that shows how to use `django-large-image` in a `girder-4` project.


### 🛠️ Customization

The mixin classes modularly designed and able to be subclassed
for your project's needs. While the provided `LargeImageFileDetailMixin` handles
`FileField`-interfaces, you can easily extend its base class,
`LargeImageDetailMixin`, to handle any mechanism of data storage in your
detail-oriented viewset.

In the following example, I will show how to use GDAL compatible VSI paths
from a model that stores `s3://` or `https://` URLs.

```py
# model.py
from django.db import models
from rest_framework import serializers


class URLImageFile(models.Model):
    name = models.TextField()
    url = models.TextField()


class URLImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLImageFile
        fields = '__all__'
```


```py
# viewsets.py
from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageDetailMixin
from django_large_image.utilities import make_vsi


class URLLargeImageMixin(LargeImageDetailMixin):
    def get_path(self, request, pk=None):
        object = self.get_object()
        return make_vsi(object.url)


class URLImageFileDetailViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    URLLargeImageMixin,
):
    queryset = models.URLImageFile.objects.all()
    serializer_class = models.URLImageFileSerializer
```

Here is a good test image: https://oin-hotosm.s3.amazonaws.com/59c66c5223c8440011d7b1e4/0/7ad397c0-bba2-4f98-a08a-931ec3a6e943.tif


#### 🥸 Non-Detail ViewSets

The `LargeImageMixin` provides a mixin interface for non-detail viewsets (no
associated model or primary key required). This can be particularly useful if
your viewset has custom logic to retrieve the desired data.

For example, you may want a viewset that gets the data path as a URL embedded
in the request's query parameters. To do this, you can make a standard ViewSet
with the `LargeImageMixin` like so:

```py
# viewsets.py
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from django_large_image.rest import LargeImageMixin
from django_large_image.utilities import make_vsi


class URLLargeImageViewSet(viewsets.ViewSet, LargeImageMixin):
    def get_path(self, request, pk=None):
        try:
            url = request.query_params.get('url')
        except KeyError:
            raise ValidationError('url must be defined as a query parameter.')
        return make_vsi(url)

```

## 🪄 Styling

`django-large-image`'s dynamic tile serving supports band styling and making
composite images from multiple frames and/or bands of your images. This means
that you can easily create a false color image from multispectral imagery.

`django-large-image` has two styling modes:

1. A simple interface to colormap a single channel using multiple query parameters. These are the documented OpenAPI query parameters.

View a single band with a Matplotlib colormap:

```js
var thumbnailUrl = `http://localhost:8000/api/image-file/${imageId}/data/thumbnail.png?band=3&palette=viridis&min=50&max=250`;
```

2. A complex specification for styling across frames and bands to create composite images using a [JSON specification defined by `large-image`](https://girder.github.io/large_image/tilesource_options.html#style).

Create a false color image from multiple bands in the source image:

```js
// See https://girder.github.io/large_image/tilesource_options.html#style
var style = {
  bands: [
    {band: 5, palette: ['#000', '#f00']},  // red
    {band: 3, palette: ['#000', '#0f0']},  // green
    {band: 2, palette: ['#000', '#00f']}   // blue
  ]
};
var styleEncoded = encodeURIComponent(JSON.stringify(style))
var thumbnailUrl = `http://localhost:8000/api/image-file/${imageId}/data/thumbnail.png?style=${styleEncoded}`;
```


## ☁️ Converting Images to Pyramidal Tiffs (COGs)

Install [`large_image_converter`](https://pypi.org/project/large-image-converter/) and run the following:

```py
import large_image_converter
large_image_converter.convert(input_path, output_path)
```

It's that easy! The default parameters for that function will convert
geospatial rasters to Cloud Optimized GeoTiffs (COGs) and non-geospatial images
to a pyramidal tiff format.

It's quite common to have a celery task that converts an image from a
model in your application. Here is a starting point:

```py
import os
from example.core import models
from celery import shared_task
import large_image_converter


@shared_task
def task_convert_cog(my_model_pk):
    image_file = models.ImageFile.objects.get(pk=my_model_pk)
    input_path = image_file.file.name  # TODO: get full path to file on disk

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'converted.tiff')
        large_image_converter.convert(input_path, output_path)

        # Do something with converted tiff file at `output_path`
        ...
```


## Demo App

There is a vanilla Django project in the `demo/` directory and this app
is published as a standalone Docker image that anyone can try out:

```bash
docker run -it -p 8000:8000 -v dli_demo_data:/opt/django-project/data ghcr.io/girder/django-large-image-demo:latest
```


## Using with django-raster

[`django-raster`](https://github.com/geodesign/django-raster) is a popular
choice for storing geospatial raster data in Django. `django-large-image` works
well with `django-raster` to provide additional endpoints for dynamic tile
serving and more.

Please take a look at the demo project here: https://github.com/ResonantGeoData/django-raster-demo
and raise any questions about usage with `django-raster` there.
