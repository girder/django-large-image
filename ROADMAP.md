# Roadmap

Our primary goal is to get through phases 1 and 2, focusing on tile serving of
large geospatial images specifically in Cloud Optimized GeoTiff (COG) format.

### Phase 1

- [x] Abstract API View classes that can be mixed-in downstream to expose all available endpoints
  - [x] endpoints for metadata (/metadata, /tiles/metadata_internal)
  - [x] endpoints for serving tiles (/tiles/zxy, /tiles/fzxy)
  - [x] cache management - tile sources should be cached so that we don't open a file for each tile
  - [x] endpoint for regions
  - [x] endpoint for thumbnails
  - [x] thumbnail caching
  - [x] endpoint for individual pixels
  - [x] endpoint for histograms
  - [x] some diagnostic and settings endpoints (list available sources, set whether to automatically use large_images and the size of small images that can be used)
- [x] Support for django's FileField
- [x] Support for S3FileField
- [x] Ship an easily extensible SSR template for tile viewing with CesiumJS
- [x] Support for using file URLs with GDAL's VSI
- [x] Provide OpenAPI documentation in swagger

### Phase 2

- [x] Support full styling for large-image
- [x] utilize this app in ResonantGeoData
- [x] utilize in non-geospatial app (Atlascope)
- [x] Support GeoDjango's [`GDALRaster`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster)
- [x] Provide admin widget
- [x] Support both detail and non-detail viewsets
- [x] Provide overridable interface to make highly customizable
- [x] Documentation (see README)
- [x] mypy typing
- [x] Error handling in REST interface


### Phase 3 and onward

- [ ] Provide universal, includable UI for building style JSON
- [ ] Provide some sort of endpoint to check if an image is a valid COG
- [ ] Tie large-image's caching into Django's cache (might require upstream work in large-image)

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
