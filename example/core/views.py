from django.views.generic import DetailView

from example.core import models


class ImageFileDetailView(DetailView):
    model = models.ImageFile


class S3ImageFileDetailView(DetailView):
    model = models.S3ImageFile
