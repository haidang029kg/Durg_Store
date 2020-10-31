from config.settings.settings_base_log import *
from config.settings.settings_base import *

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]
# tricks to have debug toolbar when developing with docker
# if os.environ.get('USE_DOCKER') == 'yes':
#     ip = socket.gethostbyname(socket.gethostname())
#     INTERNAL_IPS += [ip[:-1] + "1"]
