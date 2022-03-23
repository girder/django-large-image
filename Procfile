release: ./project/manage.py migrate
web: gunicorn --bind 0.0.0.0:$PORT --pythonpath project example.wsgi
