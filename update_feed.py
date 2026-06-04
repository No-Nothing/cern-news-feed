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

# FUNKTIONIERENDE CERN-RSS-FEEDS
RSS_FEEDS = [
    "https://home.cern/api/news/feed.rss",      # Haupt-News
    "https://home.cern/api/press/feed.rss",     # Pressemitteilungen
    "https://home.cern/api/events/feed.rss",    # Events
    "https://openlab.cern/news/feed"            # Openlab
]

entries = []

def load_rss(url):
    try:
        xml = requests.get(url, timeout=15).text
        root = ET.fromstring(xml)

        # Namespace-Handling
        ns = {}
        for k, v in root.attrib.items():
            if "xmlns" in k:
                ns[k.replace("xmlns:", "")] = v

        channel = root.find("channel")
        if channel is None:
            # Fallback: Suche mit Namespace
            channel = root.find("rss:channel", ns)

        if channel is None:
            print(f"Kein <channel> in {url}")
            return

        # Items finden (mit und ohne Namespace)
        items = channel.findall("item")
        if not items:
            items = channel.findall("rss:item", ns)

        for item in items:
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            desc = item.findtext("description") or ""
            date = item.findtext("pubDate") or datetime.now(timezone.utc).isoformat()

            entries.append({
                "title": translate(title),
                "link": link,
                "desc": translate(desc),
                "date": date
            })

    except Exception as e:
        print(f"Fehler bei {url}: {e}")

# Alle RSS-Feeds laden
for f in RSS_FEEDS:
    load_rss(f)

# Sortieren nach Datum
entries.sort(key=lambda x: x["date"], reverse=True)

# Feed erzeugen
fg = FeedGenerator()
fg.id("https://home.cern")
fg.title("CERN Superfeed – Deutsch")
fg.link(href="https://home.cern", rel="alternate")
fg.description("Kombinierter CERN‑Superfeed aus News, Press Releases, Events und Openlab")
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
