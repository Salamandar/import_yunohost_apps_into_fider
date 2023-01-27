#!/usr/bin/env python3

from datetime import datetime
import re
import psycopg2


class FiderDB():
    def __init__(self, hostname: str, username: str, password: str, dbname: str) -> None:
        self.conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
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
        cursor.execute(
            """
                INSERT INTO posts (title, slug, number, description, tenant_id, user_id, created_at, status)
                VALUES ($1, $2, (SELECT COALESCE(MAX(number), 0) + 1 FROM posts p WHERE p.tenant_id = $4),
                    $3, $4, $5, $6, 0)
                RETURNING id
            """,
            (title, self.slug_of(title), description, self.tenantid, self.userid, datetime.now())
        )
        return cursor.fetchone()[0]

    def set_as_completed(self, post_id: int, reply: str):
        self.conn.cursor().execute(
            """
                UPDATE posts
                SET response = $3, original_id = NULL, response_date = $4, response_user_id = $5, status = $6
                WHERE id = $1 and tenant_id = $2
            """,
            (post_id, self.tenantid, reply, datetime.now(), self.userid, 2)
        )

    def tag_from_slug(self, tag_slug: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, slug, color, is_public FROM tags WHERE tenant_id = $1 AND slug = $2",
            self.tenantid, tag_slug
        )
        return cursor.fetchone()[0]

    def tag_as_new_app(self, post_id: int):
        self.conn.cursor().execute(
            """
                INSERT INTO post_tags (tag_id, post_id, created_at, created_by_id, tenant_id)
                VALUES ($1, $2, $3, $4, $5)
            """,
            (self.tag_new_app, post_id, datetime.now(), self.userid, self.tenantid)
        )
