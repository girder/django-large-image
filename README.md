# django-large-image

[![PyPI](https://img.shields.io/pypi/v/django-large-image.svg?logo=python&logoColor=white)](https://pypi.org/project/django-large-image/)
[![codecov](https://codecov.io/gh/ResonantGeoData/django-large-image/branch/main/graph/badge.svg?token=VBK1F6JWNY)](https://codecov.io/gh/ResonantGeoData/django-large-image)
[![Tests](https://github.com/ResonantGeoData/django-large-image/actions/workflows/ci.yml/badge.svg)](https://github.com/ResonantGeoData/django-large-image/actions/workflows/ci.yml)

***Image tile serving in Django made easy***

`django-large-image` is an abstraction of [`large-image`](https://github.com/girder/large_image)
for use with `django-rest-framework` providing view mixins for endpoints to
work with large images in Django -- specifically geared towards geospatial and
medical image tile serving.

*Created by Kitware, Inc.*

![admin-interface](https://raw.githubusercontent.com/ResonantGeoData/django-large-image/main/doc/admin.png)

| OpenAPI Documentation | Tiles Endpoint |
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
- Admin interface widget for viewing image tiles.
- Caching - tile sources are cached for rapid file re-opening
  - tiles and thumbnails are cached to prevent recreating these data on multiple requests
- Easily extensible SSR templates for tile viewing with CesiumJS and GeoJS
- OpenAPI specification

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

Simply install the app and mixin the `LargeImageViewMixin` class to your existing
`django-rest-framework` viewsets and specify the `FILE_FIELD_NAME` as the
string name of the `FileField` in which your image data are saved.

```py
# settings.py
INSTALLED_APPS = [
    ...,
    'django_large_image',
]
```


```py
# viewsets.py
from django_large_image.rest import LargeImageViewMixin

class MyModelViewset(viewsets.GenericViewSet, LargeImageViewMixin):
  ...  # configuration for your model's viewset
  FILE_FIELD_NAME = 'field_name'
```

And that's it!

### Example Code

To use the mixin classes provided here, create a model, serializer, and view in
your Django project like so:

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

Then create the viewset, mixing in the `django-large-image` view class:
```py
# viewsets.py
from example.core import models
from rest_framework import mixins, viewsets

from django_large_image.rest import LargeImageViewMixin


class ImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    LargeImageViewMixin,
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer

    # for `django-large-image`: the name of the image FileField on your model
    FILE_FIELD_NAME = 'file'
```

Then register the URLs:

```py
# urls.py
from django.urls import path
from example.core.viewsets import ImageFileDetailView
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/image-file', ImageFileDetailView, basename='image-file')

urlpatterns = [
  path('', include('django_large_image.urls')),  # Additional diagnostic URLs from django-large-image
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


### Customization

The `LargeImageViewMixin` is modularly designed and able to be subclassed for your
project's needs. While the provided `LargeImageViewMixin` handles
`FileFeild`-interfaces, you can easily extend it to handle any mechanism of
data storage.

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

from django_large_image.rest import LargeImageViewMixin
from django_large_image.utilities import make_vsi


class URLLargeImageViewMixin(LargeImageViewMixin):
    def get_path(self, request, pk):
        object = self.get_object()
        return make_vsi(object.url)


class URLImageFileDetailView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    URLLargeImageViewMixin,
):
    queryset = models.URLImageFile.objects.all()
    serializer_class = models.URLImageFileSerializer
```

Here is a good test image: https://oin-hotosm.s3.amazonaws.com/59c66c5223c8440011d7b1e4/0/7ad397c0-bba2-4f98-a08a-931ec3a6e943.tif
