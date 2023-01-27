#!/usr/bin/env python3

from datetime import datetime
import re
import psycopg2


class FiderDB():
    def __init__(self, hostname: str, username: str, password: str, dbname: str) -> None:
        self.conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=dbname)
        self.tenantid = 1
        self.userid = 1
        self.tag_new_app = self.tag_from_slug("new-app")

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    @staticmethod
    def slug_of(name: str) -> str:
        return re.sub('[^0-9a-zA-Z]+', '-', name.lower())

    def insert(self, title: str, description: str) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                    INSERT INTO posts (title, slug, number, description, tenant_id, user_id, created_at, status)
                    VALUES (%(title)s, %(slug)s, (SELECT COALESCE(MAX(number), 0) + 1 FROM posts p WHERE p.tenant_id = %(tenant)s),
                        %(descr)s, %(tenant)s, %(user)s, %(date)s, 0)
                    RETURNING id
                """,
                {
                    "title": title,
                    "slug": self.slug_of(title),
                    "descr": description,
                    "tenant": self.tenantid,
                    "user": self.userid,
                    "date": str(datetime.now()),
                }
            )
        except psycopg2.errors.UniqueViolation:
            print(f"WARNING: already existing app in db : {title}")
            cursor.execute("SELECT id from posts where slug like %s", self.slug_of(title))

        finally:
            return cursor.fetchone()[0]


    def set_as_completed(self, post_id: int, reply: str):
        self.conn.cursor().execute(
            """
                UPDATE posts
                SET response = %(text)s, original_id = NULL,
                response_date = %(date)s, response_user_id = %(user)s, status = %(status)s
                WHERE id = %(post)s and tenant_id = %(tenant)s
            """,
            {
                "post": post_id,
                "tenant": self.tenantid,
                "text": reply,
                "date": datetime.now(),
                "user": self.userid,
                "status": 2,
            }
        )

    def tag_from_slug(self, tag_slug: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, slug, color, is_public FROM tags WHERE tenant_id = %(tenant)s AND slug = %(slug)s",
            {
                "tenant": self.tenantid,
                "slug": tag_slug,
            }
        )
        return cursor.fetchone()[0]

    def tag_as_new_app(self, post_id: int):
        self.conn.cursor().execute(
            """
                INSERT INTO post_tags (tag_id, post_id, created_at, created_by_id, tenant_id)
                VALUES (%(tag)s, %(post)s, %(date)s, %(user)s, %(tenant)s)
            """,
            {
                "tag": self.tag_new_app,
                "post": post_id,
                "date": datetime.now(),
                "user": self.userid,
                "tenant": self.tenantid,
            }
        )
