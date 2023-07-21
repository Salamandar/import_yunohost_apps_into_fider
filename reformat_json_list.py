#!/usr/bin/env python3
"""
This script expects apps.json to be filled by https://tableconvert.com/markdown-to-json
"""

# import re
import json
from typing import Dict, Tuple, Optional

import markdown
from lxml import etree


def text_to_link(text: str) -> Tuple[str, Optional[str]]:
    """[text](link) -> text, link"""
    try:
        doc = etree.fromstring(markdown.markdown(text))
        links = doc.xpath("//a")
        return links[0].text, links[0].get("href")
    except Exception:
        return text, None


def reformat_app(app: Dict[str, str]) -> Dict[str, str]:
    """Reformats the apps objets"""
    if "" in app.keys():
        del app[""]

    name, url = text_to_link(app["Name"])

    return {
        "name": name,
        "description": app.get("Description", ""),
        "project_url": url or "",
        "upstream": text_to_link(app["Upstream"])[1] or app["Upstream"],
        "package_draft": text_to_link(app["Upstream"])[1] or app["Package draft"],
    }


def main():
    with open("wishlist.json", encoding="utf-8") as apps_json:
        apps = json.load(apps_json)

    assert isinstance(apps, list), "apps.json should be a list!"

    apps = [reformat_app(app) for app in apps]

    with open("wishlist_formatted.json", "w", encoding="utf-8") as apps_json:
        apps_json.write(json.dumps(apps, indent=4))


if __name__ == "__main__":
    main()
