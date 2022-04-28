from myimages.imagefiles.models import ImageFile
import factory.django


class ImageFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageFile

    file = factory.django.FileField()
