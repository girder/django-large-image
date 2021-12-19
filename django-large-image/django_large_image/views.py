from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django_large_image import models


class ImageDetailView(LoginRequiredMixin, DetailView):

    model = models.Image

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
