from django.urls import path
from example.core import views
from example.core.viewsets import (
    ImageFileDetailView,
    S3ImageFileDetailView,
    S3VSIImageFileDetailView,
    URLImageFileDetailView,
)
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/image-file', ImageFileDetailView, basename='image-file')
router.register(r'api/vsi-image-file', ImageFileDetailView, basename='vsi-image-file')
router.register(r'api/s3-image-file', S3ImageFileDetailView, basename='s3-image-file')
router.register(r'api/s3-vsi-image-file', S3VSIImageFileDetailView, basename='s3-vsi-image-file')
router.register(r'api/url-image-file', URLImageFileDetailView, basename='url-image-file')

urlpatterns = [
    path('image-file/<int:pk>/', views.ImageFileDetailView.as_view(), name='image-file-detail'),
    path(
        's3-image-file/<int:pk>/',
        views.S3ImageFileDetailView.as_view(),
        name='s3-image-file-detail',
    ),
    path(
        'image-file/<int:pk>/viewer', views.ImageFileViewerView.as_view(), name='image-file-viewer'
    ),
    path(
        's3-image-file/<int:pk>/viewer',
        views.S3ImageFileViewerView.as_view(),
        name='s3-image-file-viewer',
    ),
    path('', views.ImageFileListView.as_view(), name='image-list'),
    path('s3', views.S3ImageFileListView.as_view(), name='s3-image-list'),
] + router.urls
