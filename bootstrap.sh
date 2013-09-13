#!/bin/bash

if [ ! -d "env" ]; then
    virtualenv -p /usr/bin/python3 --no-site-packages env
fi
source env/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cat > overmind/overmind/settings/local.py <<EOF
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
)
EOF
python overmind/manage.py syncdb --noinput
