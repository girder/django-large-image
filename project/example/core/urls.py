from django.urls import path
from example.core import views
from example.core.viewsets import ImageFileDetailView, S3ImageFileDetailView
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/large-image', ImageFileDetailView, basename='large-image')
router.register(r'api/large-image-s3', S3ImageFileDetailView, basename='large-image-s3')

urlpatterns = [
    path('large-image/<int:pk>/', views.ImageFileDetailView.as_view(), name='image-file-detail'),
    path(
        'large-image/s3/<int:pk>/',
        views.S3ImageFileDetailView.as_view(),
        name='s3-image-file-detail',
    ),
] + router.urls
