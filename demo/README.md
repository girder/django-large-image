# Simple Demo Project

The directory has a simple demo Django project with a vanilla FileField
for storing images.

Install from root directory
```
pip install --find-links https://girder.github.io/large_image_wheels \
  -e . \
  gunicorn \
  whitenoise \
  pytest \
  pytest-django \
  pytest-factoryboy
```

Run from `demo` directory
```
cd ./demo/

rm -rf ./data && mkdir ./data

python manage.py migrate
python manage.py collectstatic --noinput

DJANGO_SUPERUSER_PASSWORD=password python manage.py createsuperuser --noinput --username 'admin' --email 'admin@kitware.com'

# Test before finishing build
DJANGO_SETTINGS_MODULE=myimages.settings pytest -v

python manage.py runserver
```
