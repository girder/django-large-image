import factory.django

from myimages.imagefiles.models import ImageFile


class ImageFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageFile

    file = factory.django.FileField()
