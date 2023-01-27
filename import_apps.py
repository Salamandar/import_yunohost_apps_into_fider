#!/usr/bin/env python3

import re
import json
import yaml
import psycopg2


def connect_db():
    hostname = "localhost"
    with open("/etc/yunohost/apps/fider/settings.yml", encoding="utf-8") as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.SafeLoader)
        username = settings["db_name"]
        database = settings["db_name"]
        password = settings["psqlpwd"]
    conn = psycopg2.connect(
        f"host={hostname} user={username} password={password} dbname={database}")
    return conn


def commit_and_close_db(conn):
    conn.commit()
    conn.close()


def insert_app(conn, app):
    insert_post_sql = """
        insert into posts
        (title, description, slug, tenant_id, created_at, user_id, number, status)
        values (
            %(name)s, %(description)s, %(name_slug)s,
            1, '2023-01-19 23:00:00.0000+01', 1, (SELECT MAX(number)+1 FROM posts), 0
        );
    """

    name = f"New app: {app['name']}"

    description = f"{app['description']}"
    if url := app["url"]:
        description += f"\nProject url: {url}"
    if upstream := app["upstream"]:
        description += f"\nUpstream source code: {upstream}"

    slug = re.sub('[^0-9a-zA-Z]+', '-', name.lower())

    conn.cursor().execute(
        insert_post_sql,
        {"name": name, "description": description, "name_slug": slug}
    )


def main():
    conn = connect_db()

    with open("apps_formatted.json", encoding="utf-8") as apps_json:
        apps = json.load(apps_json)

    for app in apps:
        insert_app(conn, app)

    commit_and_close_db(conn)


if __name__ == "__main__":
    main()
