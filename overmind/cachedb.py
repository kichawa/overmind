import socket
import pickle
import yaml
import threading


class CachedbError(Exception): pass
class UnexpectedResponse(CachedbError): pass
class Disconnected(CachedbError): pass



class YamlSerializer:
    "Debug only serializer"
    def load(self, data):
        return yaml.load(data.decode('utf8'))

    def dump(self, item):
        return yaml.dump(item).encode('utf8')


class PickleSerializer:
    def load(self, data):
        return pickle.loads(data)

    def dump(self, item):
        return pickle.dumps(item)


class Cache:
    "Single cachedb server connection"
    def __init__(self, address, serializer=PickleSerializer):
        self.address = address
        self._local = threading.local()
        self.serializer = serializer()

    @property
    def _conn(self):
        if not hasattr(self._local, 'conn'):
            host, port = self.address.split(':')
            self._local.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._local.conn.connect((host, int(port)))
        return self._local.conn

    @property
    def _rd(self):
        if not hasattr(self._local, 'rd'):
            self._local.rd = self._conn.makefile('rb', newline='\r\n')
        return self._local.rd

    def _readline(self):
        line = self._rd.readline()
        if not line:
            raise Disconnected()
        return line[:-2]

    def get(self, key, default=None):
        cmd = 'get {}\r\n'.format(key)
        self._conn.send(cmd.encode('utf8'))
        resp = self._readline()
        if resp == b'NOT_FOUND':
            return default
        # VALUE <name> <size>
        _, size_str = resp.decode('iso-8859-1').rsplit(' ', 1)
        size = int(size_str)
        data = self._rd.read(size + 2)
        return self.serializer.load(data[:-2])

    def set(self, key, item, timeout=0, groups=()):
        value = self.serializer.dump(item)
        if groups:
            cmd = 'set {} {} {} {}\r\n'.format(key, len(value), timeout, ' '.join(groups))
        else:
            cmd = 'set {} {} {}\r\n'.format(key, len(value), timeout)
        self._conn.send(cmd.encode('utf8'))
        self._conn.send(value)
        self._conn.send(b'\r\n')
        resp = self._readline()
        if resp == b'STORED':
            return True
        raise UnexpectedResponse(resp)

    def delete_key(self, key):
        cmd = 'del {}\r\n'.format(key)
        self._conn.send(cmd.encode('utf8'))
        resp = self._readline()
        if resp == b'OK':
            return True
        if resp == b'NOT_FOUND':
            return False
        raise UnexpectedResponse(resp)

    def delete_group(self, group):
        cmd = 'delgrp {}\r\n'.format(group)
        self._conn.send(cmd.encode('utf8'))
        resp = self._readline()
        if resp == b'OK':
            return True
        raise UnexpectedResponse(resp)

    def ping(self):
        self._conn.send(b'ping\r\n')
        resp = self._readline()
        if resp != b'PONG':
            raise UnexpectedResponse(resp)
        return True

    def getset(self, key, default=None, timeout=0.2):
        # TODO
        return self.get(key, default)
