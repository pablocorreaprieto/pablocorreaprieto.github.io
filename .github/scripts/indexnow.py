#!/usr/bin/env python3
"""Submit pages of pablocorreaprieto.ch to IndexNow (Bing, Yandex, Seznam, Naver).

Run by .github/workflows/indexnow.yml after each GitHub Pages deploy of main.

  indexnow.py changed   pages the deployed commit added, changed or deleted (default)
  indexnow.py all       every URL in sitemap.xml

The first deploy that adds the key file submits every sitemap URL once.
Google does not use IndexNow; Search Console stays the route for Google.
"""
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

HOST = "pablocorreaprieto.ch"
KEY = "e04a684de3418416b66632ab0593cd72"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
NOT_PAGES = re.compile(r"^(404\.html|google[0-9a-f]+\.html|tools/.*|\.github/.*)$")


def url_for(path: str) -> str:
    """Repository path of an HTML file -> its public, extensionless URL."""
    if path == "index.html":
        return f"https://{HOST}/"
    if path.endswith("/index.html"):
        return f"https://{HOST}/{path[: -len('index.html')]}"
    return f"https://{HOST}/{path[: -len('.html')]}"


def sitemap_urls() -> list[str]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.parse("sitemap.xml").getroot()
    return [u.find("s:loc", ns).text.strip() for u in root.findall("s:url", ns)]


def changed_urls() -> list[str]:
    files = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AMD", "HEAD^1", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    if f"{KEY}.txt" in files:
        print("Key file is new in this deploy: submitting every sitemap URL once.")
        return sitemap_urls()
    pages = [f for f in files if f.endswith(".html") and not NOT_PAGES.match(f)]
    return [url_for(f) for f in pages]


def main() -> None:
    scope = sys.argv[1] if len(sys.argv) > 1 else "changed"
    if scope not in ("changed", "all"):
        sys.exit(f"unknown scope {scope!r}; use 'changed' or 'all'")
    urls = sorted(set(sitemap_urls() if scope == "all" else changed_urls()))
    if not urls:
        print("No page changed in this deploy; nothing to submit.")
        return
    payload = {"host": HOST, "key": KEY, "keyLocation": KEY_LOCATION, "urlList": urls}
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow answered {response.status} for {len(urls)} URL(s):")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:300]
        sys.exit(f"IndexNow answered {error.code}: {detail}")
    for url in urls:
        print(" ", url)


if __name__ == "__main__":
    main()
