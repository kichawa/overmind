from django.conf import settings

import cachedb


# cache only those response objects that response_code is in following set
CACHABLE_RESPONSE_CODE = {200, 301, 404}


if getattr(settings, 'HTTP_CACHE', False):
    serializer = cachedb.PickleSerializer
    if settings.DEBUG:
        serializer = cachedb.YamlSerializer
    cache = cachedb.Cache(settings.CACHEDB_ADDRESS, serializer=serializer)
else:
    cache = None



def expire_group(name):
    if not getattr(settings, 'HTTP_CACHE', False):
        return
    cache.delete_group(name)


def expire_groups(names):
    if not getattr(settings, 'HTTP_CACHE', False):
        return
    for name in names:
        cache.delete_group(name)
