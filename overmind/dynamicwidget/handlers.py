import re

from django.conf import settings
from django.utils import importlib


class Handlers:
    def __init__(self):
        self._handlers = {}

    def find(self, widget_id):
        for rx, fn in self._handlers.values():
            match = rx.match(widget_id)
            if match:
                return fn, match.groupdict()
        return None, {}

    def register(self, rx, handler):
        if rx in self._handlers:
            _, fn = self._handlers[rx]
            msg = "Handler for '{}' already registered: {}".format(rx, fn)
            raise Exception(msg)
        self._handlers[rx] = (re.compile(rx), handler)

    def autodiscover(self):
        for app in settings.INSTALLED_APPS:
            module_name = '{}.widgets'.format(app)
            try:
                importlib.import_module(module_name)
            except ImportError:
                pass



default = Handlers()
