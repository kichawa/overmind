from django.conf import settings
from django.core.cache import get_cache
from django.utils.importlib import import_module


class Cache:
    def __init__(self, cache):
        self.cache = cache

    def increment(self, *keys, value=1):
        res = {}
        for key in keys:
            try:
                res[key] = self.cache.incr(key, value)
            except ValueError:
                self.cache.set_many({key: value})
                res[key] = value
        return res

    def decrement(self, *keys, value=1):
        res = {}
        for key in keys:
            try:
                res[key] = self.cache.decr(key, value)
            except ValueError:
                self.cache.set_many({key: -value})
                res[key] = -value
        return res

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
