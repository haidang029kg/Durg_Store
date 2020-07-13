#!/bin/sh

cd /app
celery -A app.core beat
