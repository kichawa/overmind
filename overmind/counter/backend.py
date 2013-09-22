from django.core.cache import get_cache
from django.conf import settings
from django.utils.importlib import import_module


class Cache:
    def __init__(self, cache):
        self.cache = cache

    def increment(self, *keys, value=1):
        return {key: self.cache.incr(key, value) for key in keys}

    def decrement(self, *keys, value=1):
        return {key: self.cache.decr(key, value) for key in keys}

    def delete(self, *keys):
        self.cache.delete_many(keys)

    def get(self, *keys):
        return self.cache.get_many(keys)

    def set(self, **pairs):
        self.cache.set_many(pairs)


class DjangoCache(Cache):
    def __init__(self, cache=None):
        if not cache:
            cache = 'default'
        if isinstance(cache, str):
            cache = get_cache(cache)
        self.cache = cache


def default():
    cls_path = getattr(settings, 'COUNTER_STORAGE_BACKEND',
                       'counter.backend.DjangoCache')
    path, clsname = cls_path.rsplit('.', 1)
    module = import_module(path)
    cls = getattr(module, clsname)
    return cls()
