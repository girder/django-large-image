from django.urls import path
from example.core import views
from example.core.viewsets import (
    ImageFileDetailViewSet,
    S3ImageFileDetailViewSet,
    S3VSIImageFileDetailViewSet,
    URLImageFileDetailViewSet,
    URLLargeImageViewSet,
)
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/image-file', ImageFileDetailViewSet, basename='image-file')
router.register(r'api/vsi-image-file', ImageFileDetailViewSet, basename='vsi-image-file')
router.register(r'api/s3-image-file', S3ImageFileDetailViewSet, basename='s3-image-file')
router.register(r'api/s3-vsi-image-file', S3VSIImageFileDetailViewSet, basename='s3-vsi-image-file')
router.register(r'api/url-image-file', URLImageFileDetailViewSet, basename='url-image-file')
router.register(r'api/url-param', URLLargeImageViewSet, basename='url-param')

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
