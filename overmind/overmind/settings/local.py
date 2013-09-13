from .base import *

DEBUG = True

ALLOWED_HOSTS = (
    '127.0.0.1',
)
INTERNAL_IPS = ALLOWED_HOSTS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'overmind_db.sqlite3'),
    }
}


MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
)

INTERCEPT_REDIRECTS = False
