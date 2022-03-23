from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from example.core import models


class ImageFileDetailView(LoginRequiredMixin, DetailView):
    model = models.ImageFile


class S3ImageFileDetailView(LoginRequiredMixin, DetailView):
    model = models.S3ImageFile


class ImageFileListView(LoginRequiredMixin, ListView):
    model = models.ImageFile


class S3ImageFileListView(LoginRequiredMixin, ListView):
    model = models.S3ImageFile
