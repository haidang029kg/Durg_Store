from .settings_base import *


DEBUG = False

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware', ]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default='127.0.0.1')
ALLOWED_HOSTS = ['*']
# DATABASES
# ------------------------------------------------------------------------------
# DATABASES['default'] = env.db('DATABASE_URL')  # noqa F405
DATABASES['default']['ATOMIC_REQUESTS'] = True  # noqa F405
DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)  # noqa F405
