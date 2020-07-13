"""
ASGI config for DrugStore project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

module = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.settings_dev')
print('========== ASGI: ', module)
application = get_asgi_application()
