import getpass
import psycopg2
import sys
import sqlite3



sqlt_db_path = sys.argv[1]


def copy_users(pg_connection):
    pg_c = pg_connection.cursor()
    pg_c.execute('''
        SELECT
            id, username, first_name, last_name, last_login, email,
            date_joined
        FROM
            auth_user
    ''')

    sqlt_connection = sqlite3.connect(sqlt_db_path)
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
    sqlt_connection.commit()


def copy_topics(pg_connection):
    pg_c = pg_connection.cursor()
    pg_c.execute('''
    SELECT
        id, user_id, name, created
    FROM
        djangobb_forum_topic
    ''')

    sqlt_connection = sqlite3.connect(sqlt_db_path)
    sqlt_c = sqlt_connection.cursor()
    for row in pg_c:
        sqlt_c.execute('INSERT INTO forum_topic(id, author_id, subject, created, updated) VALUES ($1, $2, $3, $4, $4)', row)
    pg_c.close()
    sqlt_connection.commit()


def copy_posts(pg_connection):
    pg_c = pg_connection.cursor()
    pg_c.execute('''
    SELECT
        id, topic_id, user_id, body, created
    FROM
        djangobb_forum_post
    ''')

    sqlt_connection = sqlite3.connect(sqlt_db_path)
    sqlt_c = sqlt_connection.cursor()
    for row in pg_c:
        sqlt_c.execute('INSERT INTO forum_post(id, topic_id, author_id, content, created) VALUES (?, ?, ?, ?, ?)', row)
    pg_c.close()
    sqlt_connection.commit()



def main():
    pg_conn = psycopg2.connect(
            dbname="pg_5908", user="pg_5908u", host='archlinux.megiteam.pl',
            port=5435, password=getpass.getpass('archlinux database password:'))
    copy_users(pg_conn)
    copy_topics(pg_conn)
    copy_posts(pg_conn)
    pg_conn.close()

if __name__ == "__main__":
    main()