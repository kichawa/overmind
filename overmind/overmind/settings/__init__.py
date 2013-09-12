from .base import *

if os.path.isfile(os.path.join(BASE_DIR, 'overmind/settings/local.py')):
    from .local import *
