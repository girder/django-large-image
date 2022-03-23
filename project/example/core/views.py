from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from example.core import models


class ImageFileDetailView(LoginRequiredMixin, DetailView):
    model = models.ImageFile


class S3ImageFileDetailView(LoginRequiredMixin, DetailView):
    model = models.S3ImageFile


class ImageFileViewerView(LoginRequiredMixin, DetailView):
    model = models.ImageFile
    template_name = 'core/imagefile_viewer.html'


class S3ImageFileViewerView(LoginRequiredMixin, DetailView):
    model = models.S3ImageFile
    template_name = 'core/s3imagefile_viewer.html'


class ImageFileListView(LoginRequiredMixin, ListView):
    model = models.ImageFile


class S3ImageFileListView(LoginRequiredMixin, ListView):
    model = models.S3ImageFile
