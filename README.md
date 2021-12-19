# Django Large Image

Models and endpoints for working with large images in Django -- specifically
geared towards geospatial tile serving.

*DISCLAIMER:* this is a work in progress and is currently in an experimental phase.


- [x] endpoints for metadata (/tiles, /tiles/internal_metadata)
- [x] endpoints for serving tiles (/tiles/zxy, /tiles/fzxy)
- [x] cache management - tile sources should be cached so that we don't open a file for each tile
- [x] endpoint for regions
- [x] endpoint for thumbnails
- [x] thumbnail caching
- [x] endpoint for individual pixels
- [x] endpoint for histograms
- [x] some diagnostic and settings endpoints (list available sources, set whether to automatically use large_images and the size of small images that can be used)


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
