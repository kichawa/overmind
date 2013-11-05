Incomplete, debug only cachedb implementetion
=============================================

Cachedb is in memory key-value storage with ability to set and expire groups
of keys.

This (python) implementation is for pure debug purpose. It's missing some
functionalities (`getset` command, lru cache, statistics).
It's using separate thread for every connected client and single, global
storage lock shared between clients to prevent race conditions.



Protocol
========

Every line ends with `\r\n`. Except of `<value>` which is binary data, every
other part of the message has to be build using valid ascii strings, separated
with space.


get
---

Get value by it's key

    client: get <key>\r\n

If value does not exist, server will respond with `NOT_FOUND`:

    server: NOT_FOUND\r\n

else,

    server: VALUE <key> <value length>\r\n
            <value>\r\n

Returned `value length` *does not* include final `\r\n`, because it's part of
the protocol, not the value.


getset
------

*Not Implemented*

Get value by it's key and if value does not exist, notify database that we're
going to generate it's value. This should help prevent thundering herd
scenario.

    client getset <key> [<timeout>]\r\n

Server response is exactly the same as with `get` command. In addition, if
`NOT_FOUND` was returned, server should block all other `get` and `getset`
responses for given `<key>` and wait for current client to set the value
first.

Timeout should be small and depending on how expensive it is to generate a
value, should never be set to more than few seconds (preferably less than 1s).


set
---

Set value with optional timeout and groups:

    client: set <key> <value length> [<timeout> [<group 1> <group 2> ...]]\r\n
            <value of length "value length">\r\n
    server: STORED\r\n


del
---

Delete value stored under given key

    client: del <key>\r\n

If key was deleted (existed):

    server: OK\r\n

otherwise:

    server: NOT_FOUND\r\n


delgrp
------

Delete all values belonging to given group

    client: delgrp <key> \r\n
    server: OK\r\n


ping
----

Web scale ping-pong implementation

    client: ping\r\n
    server: PONG\r\n


keys
----

Purely debug function that returns list of all available keys.


    client: keys\r\n

    server: <key 1>\r\n
            <key 2>\r\n
            \r\n

If there's no single key in the database, only `\r\n` is returned.
