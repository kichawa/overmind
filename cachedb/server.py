import argparse
import socket
import sys
import threading
import traceback

import storage
import handlers


DEFAULT_ENCODING = 'iso-8859-1'


def handle_client(cache_lock, cache, client):
    try:
        _handle_client(cache_lock, cache, client)
    except Exception as exc:
        traceback.print_exc(file=sys.stdout)
        client.send(b'INTERNAL_ERROR\r\n')
    finally:
        client.close()


def _handle_client(cache_lock, cache, client):
    rd = client.makefile('rb', newline='\r\n')
    while True:
        line = rd.readline()
        if not line:
            # diconnected
            return
        # cut off \r\n
        line = line[:-2]
        if not line:
            continue
        command, *rest = line.split(maxsplit=1)
        command = command.decode(DEFAULT_ENCODING)
        handler = handlers.get(command)
        if handler is None:
            client.send(b'INVALID_COMMAND\r\n')
            continue
        try:
            cache_lock.acquire()
            handler(cache, rd, client, *rest)
        finally:
            cache_lock.release()


def run_cache_server(cache, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', port))
    s.listen(1)
    cache_lock = threading.Lock()
    while True:
        client, _ = s.accept()
        t = threading.Thread(target=handle_client,
                             args=(cache_lock, cache, client))
        t.start()


def main():
    parser = argparse.ArgumentParser(description='Cachedb implementation')
    parser.add_argument('--port', type=int, default=12345, help='Server port')
    args = parser.parse_args()

    cache = storage.GroupDict()
    try:
        run_cache_server(cache, args.port)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
