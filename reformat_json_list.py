#!/usr/bin/env python3
"""
This script expects apps.json to be filled by https://tableconvert.com/markdown-to-json
"""

# import re
import json
from typing import Dict, Tuple, Optional, Any

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


def reformat_app(app: Dict[str, str]) -> None:
    """Reformats the apps objets"""
    if "" in app.keys():
        del app[""]

    app["name"], url = text_to_link(app["name"])
    app["url"] = url or ""

    app["upstream"] = text_to_link(app["upstream"])[1] or app["upstream"]
    app["package_draft"] = text_to_link(app["upstream"])[1] or app["package_draft"]


def main():
    with open("apps.json", encoding="utf-8") as apps_json:
        apps = json.load(apps_json)

    for app in apps:
        reformat_app(app)

    with open("apps_formatted.json", "w", encoding="utf-8") as apps_json:
        apps_json.write(json.dumps(apps, indent=4))


if __name__ == "__main__":
    main()
