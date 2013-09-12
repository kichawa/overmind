#!/bin/bash

if [ ! -d "env" ]; then
    virtualenv -p /usr/bin/python3 --no-site-packages env
fi
source env/bin/activate
pip install -r requirements-dev.txt
cat > overmind/overmind/settings_local.py <<EOF
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True
ALLOWED_HOSTS = (
    '127.0.0.1',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'overmind_db.sqlite3'),
    }
}
EOF
python overmind/manage.py syncdb --noinput
