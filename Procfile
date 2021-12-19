release: ./manage.py migrate
web: gunicorn --bind 0.0.0.0:$PORT example.wsgi
worker: REMAP_SIGTERM=SIGQUIT celery --app example.celery worker --loglevel INFO --without-heartbeat
