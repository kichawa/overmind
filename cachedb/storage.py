import time


class DoesNotExist(Exception):
    pass


class Group:
    __next_id = 1

    def __init__(self, name):
        self.name = name
        self.version = Group.acquire_id()

    @classmethod
    def acquire_id(cls):
        try:
            return cls.__next_id
        finally:
            cls.__next_id += 1


class Item:
    def __init__(self, key, value, timeout, groups):
        self.key = key
        self.value = value
        self.groups = groups
        if timeout:
            self.expireat = int(time.time()) + timeout
        else:
            self.expireat = None

    def is_valid(self, group_dict):
        if self.expireat and self.expireat < time.time():
            return False
        for group in self.groups:
            g = group_dict._groups.get(group.name, None)
            if not g or g.version != group.version:
                return False
        return True


class GroupDict:
    def __init__(self):
        self._items = {}
        self._groups = {}

    def _get_or_create_groups(self, names):
        groups = []
        for name in names:
            if isinstance(name, bytes):
                name = name.decode('utf8')
            group = self._groups.get(name, None)
            if not group:
                group = Group(name)
                self._groups[name] = group
            groups.append(group)
        return groups

    def get(self, key):
        item = self._items.get(key, None)
        if not item:
            raise DoesNotExist(key)
        if not item.is_valid(self):
            self._items.pop(key)
            raise DoesNotExist(key)
        return item.value

    def set(self, key, value, timeout=0, groups=()):
        if isinstance(key, bytes):
            key = key.decode('utf8')
        item = Item(key, value, timeout, self._get_or_create_groups(groups))
        self._items[key] = item

    def del_key(self, key):
        if isinstance(key, bytes):
            key = key.decode('utf8')
        item = self._items.pop(key, None)
        if not item:
            raise DoesNotExist(key)

    def del_group(self, name):
        if isinstance(name, bytes):
            name = name.decode('utf8')
        self._groups.pop(name, None)

    def keys(self):
        for key, item in self._items.items():
            if item.is_valid(self):
                yield key
