from io import open as io_open
from pathlib import Path

from setuptools import find_packages, setup

readme_file = Path(__file__).parent / 'README.md'
if readme_file.exists():
    with io_open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    # When this is first installed in development Docker, README.md is not available
    long_description = ''

setup(
    name='django-large-image',
    version='0.7.0',
    description='Dynamic tile server in Django built on top of large-image (and GDAL)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    url='https://github.com/girder/django-large-image',
    keywords='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 3.0',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python',
    ],
    python_requires='>=3.8',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django',
        'djangorestframework',
        'drf-yasg',
        'filelock',
        'large-image>=1.14',
    ],
    extras_require={
        'colormaps': [
            'matplotlib',
            'cmocean',
        ],
    },
)
