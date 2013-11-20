import logging

from django.conf import settings

import cachedb


log = logging.getLogger(__name__)


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
    try:
        cache.delete_group(name)
    except Exception as err:
        log.critical("cache connection error, cannot expire group: %s (%s)",
                     name, err)


def expire_groups(names):
    if not getattr(settings, 'HTTP_CACHE', False):
        return
    for name in names:
        try:
            cache.delete_group(name)
        except Exception as err:
            log.critical("cache connection error, cannot expire group: %s (%s)",
                         name, err)
