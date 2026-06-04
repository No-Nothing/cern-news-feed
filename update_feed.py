import os
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

os.makedirs('public', exist_ok=True)

# Übersetzung via LibreTranslate
def translate(text):
    try:
        r = requests.post(
            "https://libretranslate.de/translate",
            data={"q": text, "source": "en", "target": "de"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json().get("translatedText", text)
    except:
        pass
    return text

# Quellen
RSS_FEEDS = [
    "https://home.cern/api/press/feed.rss",
    "https://home.cern/api/events/feed.rss",
    "https://openlab.cern/news/feed"
]

JSON_FEEDS = [
    "https://home.cern/api/news",
    "https://atlas.cern/api/news",
    "https://cms.cern/api/news",
    "https://alice.cern/api/news",
    "https://lhcb.cern/api/news"
]

entries = []

# RSS verarbeiten
def load_rss(url):
    try:
        xml = requests.get(url, timeout=15).text
        root = ET.fromstring(xml)
        for item in root.find("channel").findall("item"):
            title = item.findtext("title")
            link = item.findtext("link")
            desc = item.findtext("description") or ""
            date = item.findtext("pubDate") or datetime.now(timezone.utc).isoformat()

            entries.append({
                "title": translate(title),
                "link": link,
                "desc": translate(desc),
                "date": date
            })
    except:
        pass

# JSON verarbeiten
def load_json(url):
    try:
        data = requests.get(url, timeout=15).json()
        for item in data.get("items", []):
            title = item.get("title", "")
            link = "https://home.cern" + item.get("url", "")
            desc = item.get("summary", "")
            date = item.get("date", datetime.now(timezone.utc).isoformat())

            entries.append({
                "title": translate(title),
                "link": link,
                "desc": translate(desc),
                "date": date
            })
    except:
        pass

# Alle Feeds laden
for f in RSS_FEEDS:
    load_rss(f)

for f in JSON_FEEDS:
    load_json(f)

# Sortieren nach Datum
entries.sort(key=lambda x: x["date"], reverse=True)

# Feed erzeugen
fg = FeedGenerator()
fg.id("https://home.cern")
fg.title("CERN Superfeed – Deutsch")
fg.link(href="https://home.cern", rel="alternate")
fg.description("Kombinierter CERN‑Superfeed aus News, Press Releases, Events und Experimenten")
fg.language("de")

for e in entries[:40]:
    fe = fg.add_entry()
    fe.id(e["link"])
    fe.title(e["title"])
    fe.link(href=e["link"])
    fe.description(e["desc"])
    fe.pubDate(e["date"])

fg.rss_file("public/cern_feed.xml", pretty=True)
print("CERN Superfeed erfolgreich aktualisiert.")
