#!/usr/bin/env python3

import json
import yaml

DRY_RUN = False

if not DRY_RUN:
    from fider_db import FiderDB


def main() -> None:
    if not DRY_RUN:
        with open("/etc/yunohost/apps/fider/settings.yml", encoding="utf-8") as settings_file:
            settings = yaml.load(settings_file, Loader=yaml.SafeLoader)

        fider_db = FiderDB("localhost", settings["db_name"], settings["psqlpwd"], settings["db_name"])

    all_apps = []

    # List of packaged apps
    with open("apps.json", encoding="utf-8") as apps_json:
        apps = json.load(apps_json)["apps"]

    for app in apps.values():
        all_apps.append({
            "name": app["manifest"]["name"],
            "description": app["manifest"]["description"]["en"],
            "project_url": app["manifest"].get("url", None),
            "upstream": app["manifest"].get("upstream", {}).get("code", None),
            "package_url": app["git"]["url"],
            "finished": True
        })

    # List of wishlists
    with open("wishlist_formatted.json", encoding="utf-8") as apps_json:
        apps = json.load(apps_json)

    for app in apps:
        app["finished"] = False
        all_apps.append(app)

    # Import all apps in Fider
    for app in all_apps:
        name = f"New app: {app['name']}"

        description = f"{app['description']}"

        if url := app["project_url"]:
            description += f"\nProject url: {url}"

        if upstream := app["upstream"]:
            description += f"\nUpstream source code: {upstream}"

        if DRY_RUN:
            print(name, description)

        else:
            post_id = fider_db.insert(name, description)
            fider_db.tag_as_new_app(post_id)

            if app["finished"]:
                fider_db.set_as_completed(post_id, f"Packaged at: {app['package_url']}")


if __name__ == "__main__":
    main()
