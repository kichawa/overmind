from counter import backend


class Memcache:
    "But not memcached! ;)"
    _empty = object()

    def __init__(self):
        self._mem = {}

    def incr(self, key, value=1):
        val = int(self._mem.get(key, 0))
        val += value
        self._mem[key] = val
        return val

    def decr(self, key, value=1):
        val = int(self._mem.get(key, 0))
        val -= value
        self._mem[key] = val
        return val

    def get_many(self, keys):
        res = {}
        for key in keys:
            val = self._mem.get(key, self._empty)
            if val is not self._empty:
                res[key] = val
        return res

    def set_many(self, pairs):
        self._mem.update(pairs)

    def delete_many(self, keys):
        for key in keys:
            self._mem.pop(key, None)


class Memory(backend.Cache):
    def __init__(self):
        super(Memory, self).__init__(Memcache())
