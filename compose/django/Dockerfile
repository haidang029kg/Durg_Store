FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install -r /requirements/production.txt

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/django/gunicorn.sh /gunicorn.sh
RUN chmod +x /gunicorn.sh

#COPY ./compose/django/start-dev.sh /start-dev.sh
#RUN chmod +x /start-dev.sh
#
#COPY ./compose/django/start-celery-worker.sh /start-celery-worker.sh
#RUN chmod +x /start-celery-worker.sh
#
#
#COPY ./compose/django/start-celery-beat.sh /start-celery-beat.sh
#RUN chmod +x /start-celery-beat.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
