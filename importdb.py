#!/usr/bin/env python
import getpass
import random
import re
import sqlite3
import sys

import psycopg2


sqlt_db_path = sys.argv[1]

TAGS = [
    'Beginner',
    'Installation',
    'Kernel & Hardware',
    'Desktop Environment',
    'Laptop',
    'Networking',
    'Games',
    'Multimedia',
    'Administration',
    'About forum',
    'Pacman',
    'Random',
]


_bbcode_to_markdown = (
    (re.compile(r'\[b\]((?:.|\n)+?)\[\/b\]'), r"**\1**"),
    (re.compile(r'\[u\]((?:.|\n)+?)\[\/u\]'), r"*\1*"),
    (re.compile(r'\[i\]((?:.|\n)+?)\[\/i\]'), r"*\1*"),
    (re.compile(r'\[s\]((?:.|\n)+?)\[\/s\]'), r"~~\1~~"),
    (re.compile(r'\[color\=.+?\]((?:.|\n)+?)\[\/color\]'), r"\1"),
    (re.compile(r'(\n)\[\*\]'), r"\1* "),
    (re.compile(r'\[\/*list\]'), r''),
    (re.compile(r'\[img\]((?:.|\n)+?)\[\/img\]'), r'![](\1)'),
    (re.compile(r'\[url=(.+?)\]((?:.|\n)+?)\[\/url\]'), r'[\2](\1)'),
    (re.compile(r'#'), r"\#"),
    # TODO - [quote]
    )


def code_converter(text):
    codes = re.finditer(r'\[code\]((?:.|\n)+?)\[\/code\]', text)
    changes = []
    i = 0
    a = 0 
    for res in codes:
        texta = res.string[res.start():res.end()]
        new_lines = texta.split("\n")
        stringa = "\n"
        for www in new_lines:
            stringa += "    {}".format(www)
            i += 4
        stringa += "\n\n"
        i += 3
        changes.append(((res.start() + a, res.end() + a), stringa))
        a += i
        i = 0
    for c, string in changes:
        text = text[0:c[0]] + string + text[c[1]:]
    text = re.sub(r'\[code\]((?:.|\n)+?)\[\/code\]', r"\1", text)
    return text


def quote_converter(text):
    quotes = re.findall(r'\[quote(.*?)\]((?:.|\n)+?)\[\/quote\]', text)
    changes = []
    for trash, quote in quotes:
        new_lines = quote.split("\n")
        string = "\n"
        for new_line in new_lines:
            string += "> {}".format(new_line)
        string += "\n"
        changes.append((quote, string))

    for change in changes:
        text = text.replace(change[0], change[1])
    print(text)
    text = re.sub(r'\[quote(.*?)\]((.*?|\n)+?)\[\/quote\]', r"\2", text)
    return text


def bbcode_to_markdown(text, post_id):
    for rx, repl in _bbcode_to_markdown:
        text = rx.sub(repl, text)
    text = code_converter(text)
    text = quote_converter(text)
    return text


def copy_users(pg_connection, sqlt_connection):
    pg_c = pg_connection.cursor()
    pg_c.execute('''
        SELECT
            id, username, first_name, last_name, last_login, email,
            date_joined
        FROM
            auth_user
    ''')

    sqlt_c = sqlt_connection.cursor()
    for row in pg_c:
        sqlt_c.execute('''
            INSERT INTO
                auth_user(id, username, first_name, last_name, password,
                last_login, is_superuser, email, is_staff, is_active,
                date_joined)
                VALUES (?, ?, ?, ?, '-', ?, 0, ?, 0, 1, ?)
            ''', row)
    pg_c.close()


def copy_topics(pg_connection, sqlt_connection):
    pg_c = pg_connection.cursor()
    pg_c.execute('''
    SELECT
        id, user_id, name, created, post_count
    FROM
        djangobb_forum_topic
    ''')

    sqlt_c = sqlt_connection.cursor()
    for tag in TAGS:
        sqlt_c.execute('''
            INSERT INTO forum_tag(label, description)
            VALUES (?, '')
        ''', (tag, ))
    for row in pg_c:
        sqlt_c.execute('''
            INSERT INTO forum_topic(id, author_id, subject, created, updated,
                                    content_updated, response_count,
                                    is_deleted, is_closed, is_solved)
            VALUES ($1, $2, $3, $4, $4, $4, $5 - 1, 0, 0, 0)
        ''', row)
        attached_tags = {None}
        for _ in range(random.randint(1, 5)):
            tid = None
            while tid in attached_tags:
                tid = random.randint(1, len(TAGS))
            attached_tags.add(tid)

            sqlt_c.execute('''
                INSERT INTO forum_topic_tags (topic_id, tag_id )
                VALUES ($1, $2)
            ''', (row[0], tid))

    pg_c.close()


def copy_posts(pg_connection, sqlt_connection):
    pg_c = pg_connection.cursor()
    pg_c.execute('''
    SELECT
        id, topic_id, user_id, body, created, user_ip, markup
    FROM
        djangobb_forum_post
    ''')

    sqlt_c = sqlt_connection.cursor()
    for row in pg_c:
        row = list(row)
        markup = row.pop()
        if markup == 'bbcode':
            row[3] = bbcode_to_markdown(row[3], row[0])
        row.append(False)
        sqlt_c.execute('''
            INSERT INTO forum_post(id, topic_id, author_id, content, created,
                                   updated, ip, is_deleted, is_solving)
            VALUES ($1, $2, $3, $4, $5, $5, $6, $7, 0)
        ''', row)
    pg_c.close()



def main():
    if len(sys.argv) != 2:
        sys.exit("""
Usage:
    python3 {} <path to sqlite3 database file>

Important: database has to be initialized but empty.
        """.format(sys.argv[0]))
    global sqlt_db_path
    sqlt_db_path = sys.argv[1]

    pg_conn = psycopg2.connect(
            dbname="pg_5908", user="pg_5908u", host='archlinux.megiteam.pl',
            port=5435, password=getpass.getpass('archlinux database password:'))
    sqlt_connection = sqlite3.connect(sqlt_db_path)
    copy_users(pg_conn, sqlt_connection)
    copy_topics(pg_conn, sqlt_connection)
    copy_posts(pg_conn, sqlt_connection)
    pg_conn.close()
    sqlt_connection.commit()

if __name__ == "__main__":
    main()
