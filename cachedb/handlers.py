import storage


DEFAULT_ENCODING = 'iso-8859-1'


def get(cmd_name):
    "Return handler for given command or None if does not exist"
    if isinstance(cmd_name, bytes):
        cmd_name = cmd_name.decode('utf8')
    return command_handlers.get(cmd_name, None)


def handle_get(cache, rd, client, params=b''):
    params = params.strip()
    if not params:
        client.send(b'MISSING_PARAMETER\r\n')
        return
    key = params.decode(DEFAULT_ENCODING)
    try:
        value = cache.get(key)
        msg = 'VALUE {} {}\r\n'.format(key, len(value))
        client.send(msg.encode(DEFAULT_ENCODING))
        client.send(value)
        client.send(b'\r\n')
    except storage.DoesNotExist:
        client.send(b'NOT_FOUND\r\n')


def handle_set(cache, rd, client, params=None):
    chunks = params.split()

    if len(chunks) < 2:
        client.send(b'MISSING_PARAMETER\r\n')
        return

    if len(chunks) == 2:
        # <key> <len>
        key, val_len = chunks
        timeout = 0
        groups = ()
    else:
        # <key> <len> <timeout>
        # <key> <len> <timeout> [<group>, ...]
        key, val_len, timeout, *groups = chunks
        timeout = int(timeout)

    key = key.decode(DEFAULT_ENCODING)
    val_len = int(val_len)
    # + \r\n
    val = b''
    while len(val) < val_len:
        val += rd.read(val_len + 2 - len(val))
    # cut off \r\n
    val = val[:-2]
    cache.set(key, val, timeout, groups)
    client.send(b'STORED\r\n')


def handle_del(cache, rd, client, params=None):
    params = params.strip()
    if not params:
        client.send(b'MISSING_PARAMETER\r\n')
        return
    key = params.decode(DEFAULT_ENCODING)
    try:
        cache.del_key(key)
    except storage.DoesNotExist:
        client.send(b'NOT_FOUND\r\n')
    else:
        client.send(b'OK\r\n')


def handle_delgrp(cache, rd, client, params=None):
    params = params.strip()
    if not params:
        client.send(b'MISSING_PARAMETER\r\n')
        return
    name = params.decode(DEFAULT_ENCODING)
    cache.del_group(name)
    client.send(b'OK\r\n')


def handle_keys(cache, rd, client, params=None):
    line_end = b'\r\n'
    for key in cache.keys():
        client.send(key.encode(DEFAULT_ENCODING))
        client.send(line_end)
    client.send(line_end)


def handle_ping(cache, rd, client, params=None):
    client.send(b'PONG\r\n')


command_handlers = {
    'get': handle_get,
    'set': handle_set,
    'del': handle_del,
    'delgrp': handle_delgrp,
    'keys': handle_keys,
    'ping': handle_ping,
}
