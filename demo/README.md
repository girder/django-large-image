# Simple Demo Project

The directory has a simple demo Django project with a vanilla FileField
for storing images.

Install from root directory
```
pip install \
  -e . \
  large-image[rasterio,pil]>=1.22 \
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
DJANGO_SETTINGS_MODULE=myimages.settings pytest --cov=django_large_image -v .

python manage.py runserver
```
