#!/bin/sh

python ./manage.py migrate
python ./manage.py collectstatic --noinput
gunicorn -w 2 config.wsgi -b 0.0.0.0:8000
