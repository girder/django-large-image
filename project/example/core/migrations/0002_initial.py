# Generated by Django 4.0.3 on 2022-03-22 05:08

from django.db import migrations, models
import django_extensions.db.fields
import s3_file_field.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_default_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('file', models.FileField(upload_to='')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='S3ImageFile',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name='modified'
                    ),
                ),
                ('file', s3_file_field.fields.S3FileField()),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]