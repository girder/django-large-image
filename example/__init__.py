# This project module is imported for us when Django starts. To ensure that Celery app is always
# defined prior to any shared_task definitions (so those tasks will bind to the app), import
# the Celery module here for side effects.
from .celery import app as _celery_app  # noqa: F401

# Do not import anything else from this file, to avoid interfering with the startup order of the
# Celery app and Django's settings.
