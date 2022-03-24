# django-large-image

[![PyPI](https://img.shields.io/pypi/v/django-large-image.svg?logo=python&logoColor=white)](https://pypi.org/project/django-large-image/)
[![codecov](https://codecov.io/gh/ResonantGeoData/django-large-image/branch/main/graph/badge.svg?token=VBK1F6JWNY)](https://codecov.io/gh/ResonantGeoData/django-large-image)
[![Tests](https://github.com/ResonantGeoData/django-large-image/actions/workflows/ci.yml/badge.svg)](https://github.com/ResonantGeoData/django-large-image/actions/workflows/ci.yml)

*Created by Kitware, Inc.*

`django-large-image` is an abstraction of [`large-image`](https://github.com/girder/large_image)
for use with `django-rest-framework` providing view mixins for endpoints to
work with large images in Django -- specifically geared towards geospatial and
medical image tile serving.

*DISCLAIMER:* this is a work in progress and is currently in an experimental phase.

| RGB Raster | Colormapped Raster Band |
|---|---|
| ![raster](https://raw.githubusercontent.com/ResonantGeoData/django-large-image/main/doc/raster.png) | ![raster-colormap](https://raw.githubusercontent.com/ResonantGeoData/django-large-image/main/doc/raster_colormap.png) |

| Swagger Documentation | Tiles Endpoint |
|---|---|
|![swagger-spec](https://raw.githubusercontent.com/ResonantGeoData/django-large-image/main/doc/swagger.png) | ![tiles-spec](https://raw.githubusercontent.com/ResonantGeoData/django-large-image/main/doc/tiles_endpoint.png)|


## Overview

This package ports Kitware's [large-image](https://github.com/girder/large_image)
to Django by providing a set of abstract, mixin API view classes that will
handle tile serving, fetching metadata from images, and extracting regions of
interest.

`django-large-image` is an optionally installable Django app with
a few classes that can be mixed into a Django project (or application)'s
drf-based views to provide tile serving endpoints out of the box. Notably,
`django-large-image` is designed to work specifically with `FileFeild`
interfaces with development being tailored to Kitware's
[`S3FileField`](https://github.com/girder/django-s3-file-field). We are working
to also support GeoDjango's [`GDALRaster`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster)
in the future

This package ships with pre-made HTML templates for rendering geospatial image
tiles with CesiumJS and non-geospatial image tiles with [GeoJS](https://github.com/OpenGeoscience/geojs).

### Features

Rich set of RESTful endpoints to extract information from large image formats:
- Image metadata (`/metadata`, `/internal_metadata`)
- Tile serving (`/tiles/{z}/{x}/{y}.png?projection=EPSG:3857`)
- Region extraction (`/region.tif?left=v&right=v&top=v&bottom=v`)
- Image thumbnails (`/thumbnail`)
- Individual pixels (`/pixel?left=v&top=v`)
- Band histograms (`/histogram`)

Support for general FileFeild's or File URLs
- Supports django's FileFeild
- Supports [`S3FileField`](https://github.com/girder/django-s3-file-field)
- Supports GDAL's [Virtual File System](https://gdal.org/user/virtual_file_systems.html) for `s3://`, `ftp://`, etc. URLs

Miscellaneous:
- caching - tile sources are cached for rapid file re-opening
  - tiles and thumbnails are cached to prevent recreating these data on multiple requests
- Easily extensible SSR templates for tile viewing with CesiumJS and GeoJS
- OpenAPI documentation in swagger

## Installation

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
production environments. To install our GDAL wheel, use: `pip install --find-links https://girder.github.io/large_image_wheels GDAL`*


```bash
pip install \
  --find-links https://girder.github.io/large_image_wheels \
  django-large-image \
  large-image-source-gdal
```


## Usage

Simply import and mixin the `LargeImageView` class to your existing
`django-rest-framework` viewsets and specify the `FILE_FIELD_NAME` as the
string name of the `FileField` in which your image data are saved.

```py
from django_large_image.rest import LargeImageView

class MyModelViewset(viewsets.GenericViewSet, LargeImageView):
  ...  # configuration for your model's viewset
  FILE_FIELD_NAME = 'field_name'
```

And that's it!

### Example Code

To use the mixin classes provided here, create a model, serializer, and view in
your Django project like so:

```py
models.py
---
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
admin.py
---
from django.contrib import admin
from example.core.models import ImageFile


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')
```

Then create the viewset, mixing in the `django-large-image` view class:
```py
viewsets.py
---
from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageView


class ImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageView,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer

    # for `django-large-image`: the name of the image FileField on your model
    FILE_FIELD_NAME = 'file'
```

Then register the URLs:

```py
urls.py
---
from django.urls import path
from example.core.viewsets import ImageFileDetailView
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/large-image', ImageFileDetailView, basename='image-file')

urlpatterns = [
  path('', include('django_large_image.urls')),  # Some additional diagnostic URLs from django-large-image
] + router.urls

```

Please note the example Django project in the `project/` directory of this
repository that shows how to use `django-large-image`.

## Work Plan

Our primary goal is to get through phases 1 and 2, focusing on tile serving of
large geospatial images specifically in Cloud Optimized GeoTiff (COG) format.

### Phase 1

- [x] Abstract API View classes that can be mixed-in downstream to expose all available endpoints
  - [x] endpoints for metadata (/tiles, /tiles/internal_metadata)
  - [x] endpoints for serving tiles (/tiles/zxy, /tiles/fzxy)
  - [x] cache management - tile sources should be cached so that we don't open a file for each tile
  - [x] endpoint for regions
  - [x] endpoint for thumbnails
  - [x] thumbnail caching
  - [x] endpoint for individual pixels
  - [x] endpoint for histograms
  - [x] some diagnostic and settings endpoints (list available sources, set whether to automatically use large_images and the size of small images that can be used)
- [x] Support for django's FileFeild
- [x] Support for S3FileField
- [x] Ship an easily extensible SSR template for tile viewing with CesiumJS
- [x] Support for using file URLs with GDAL's VSI
- [x] Provide OpenAPI documentation in swagger

### Phase 2

- [ ] Refactor/prototpye RGD's ChecksumFile model as a FieldFile subclass
- [ ] Support GeoDjango's [`GDALRaster`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster)
- [ ] Tie large-image's caching into Django's cache (might require upstream work in large-image)
- [ ] Provide some sort of endpoint to check if an image is a valid COG

### Phase 3 and onward

Incorporate more features from large-image.

Things that would require implementing tasks with celery:

- [ ] ability to convert images via large_image_converter
- [ ] async endpoint for regions

Things I'm unsure about:

- [ ] endpoints for associated images
- [ ] ability to precache thumbnails (the thumbnail jobs endpoints)
- [ ] endpoints for serving tiles in deepzoom format

Things I think should be implemented downstream:

- endpoint or method to make / unmake a Django file field into a large_image item
- fuse-like ability to access filefields as os-level files (until implemented, s3 files will need to be pulled locally to serve them, which is inefficient)
