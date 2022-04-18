# Roadmap

Our primary goal is to get through phases 1 and 2, focusing on tile serving of
large geospatial images specifically in Cloud Optimized GeoTiff (COG) format.

### Phase 1

- [x] Abstract API View classes that can be mixed-in downstream to expose all available endpoints
  - [x] endpoints for metadata (/tiles, /tiles/metadata_internal)
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

- [ ] Handle band/component selection styling for tile serving and thumbnails
  - e.g., use channels 3,7,5 for Red Green Blue
  - endable linear/discrete color modes
- [ ] Tie large-image's caching into Django's cache (might require upstream work in large-image)
- [ ] Provide some sort of endpoint to check if an image is a valid COG
- [ ] Create a secondary app with celery tasks for converting images to COG
- [ ] Refactor/prototpye RGD's ChecksumFile model as a FieldFile subclass
- [ ] Support GeoDjango's [`GDALRaster`](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/gdal/#django.contrib.gis.gdal.GDALRaster)

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
