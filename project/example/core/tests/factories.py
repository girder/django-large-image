from django.contrib.auth.models import User
from example.core.models import ImageFile, S3ImageFile
import factory.django


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.SelfAttribute('email')
    email = factory.Faker('safe_email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class ImageFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageFile

    file = factory.django.FileField()


class S3ImageFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = S3ImageFile

    file = factory.django.FileField()
