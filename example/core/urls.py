from rest_framework.routers import SimpleRouter

from example.core.viewsets import ImageFileDetailView, S3ImageFileDetailView

router = SimpleRouter(trailing_slash=False)
router.register(r'api/large_image', ImageFileDetailView, basename='large-image')
router.register(r'api/large_image/s3', S3ImageFileDetailView, basename='large-image-s3')

urlpatterns = [] + router.urls
