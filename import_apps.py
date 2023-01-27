#!/usr/bin/env python3

from typing import Tuple
import json
import yaml

from fider_db import FiderDB

def main():
    with open("/etc/yunohost/apps/fider/settings.yml", encoding="utf-8") as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.SafeLoader)

    fider_db = FiderDB("localhost", settings["db_name"], settings["psqlpwd"], settings["db_name"])

    with open("wishlist_formatted.json", encoding="utf-8") as apps_json:
        apps = json.load(apps_json)

    for app in apps:
        name = f"New app: {app['name']}"

        description = f"{app['description']}"
        if url := app["url"]:
            description += f"\nProject url: {url}"
        if upstream := app["upstream"]:
            description += f"\nUpstream source code: {upstream}"

        post_id = fider_db.insert(name, description)
        fider_db.tag_as_new_app(post_id)

    with open("apps.json", encoding="utf-8") as apps_json:
        apps = json.load(apps_json)["apps"]

    for app in apps:
        name = app["manifest"]["name"]
        descr = app["manifest"]["description"]["en"]
        url = app["manifest"]["url"]
        source = app["manifest"]["upstream"]["code"]
        pkg_url = app["git"]["url"]

        description = f"{descr}\nProject url: {url}\nUpstream source code: {source}"

        post_id = fider_db.insert(f"New App: {name}", description)
        fider_db.tag_as_new_app(post_id)
        fider_db.set_as_completed(post_id, f"Packaged at: {pkg_url}")


if __name__ == "__main__":
    main()
