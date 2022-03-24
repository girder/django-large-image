from django.views.generic import DetailView, ListView
from example.core import models


class ImageFileDetailView(DetailView):
    model = models.ImageFile


class S3ImageFileDetailView(DetailView):
    model = models.S3ImageFile


class ImageFileViewerView(DetailView):
    model = models.ImageFile
    template_name = 'core/imagefile_viewer.html'


class S3ImageFileViewerView(DetailView):
    model = models.S3ImageFile
    template_name = 'core/s3imagefile_viewer.html'


class ImageFileListView(ListView):
    model = models.ImageFile


class S3ImageFileListView(ListView):
    model = models.S3ImageFile
