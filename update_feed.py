import os
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

# 1. Ordner erstellen
os.makedirs('public', exist_ok=True)

# 2. Offizieller CERN-Feed
CERN_FEED_URL = "https://home.cern/api/news/feed.rss"

# 3. Übersetzungsfunktion (LibreTranslate)
def translate_to_german(text):
    try:
        resp = requests.post(
            "https://libretranslate.de/translate",
            data={
                "q": text,
                "source": "en",
                "target": "de",
                "format": "text"
            },
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("translatedText", text)
    except:
        pass
    return text  # Fallback: Originaltext

print("Lade offiziellen CERN-Feed...")

try:
    response = requests.get(CERN_FEED_URL, timeout=15)
    response.raise_for_status()
    xml_data = response.text
except Exception as e:
    print(f"Fehler beim Abrufen des CERN-Feeds: {e}")
    xml_data = None

# 4. Eigenen Feed initialisieren
fg = FeedGenerator()
fg.id('https://home.cern/news')
fg.title('CERN News – Deutsch übersetzt')
fg.link(href='https://home.cern/news', rel='alternate')
fg.description('Automatisch übersetzter Feed basierend auf dem offiziellen CERN-Newsfeed')
fg.language('de')

articles_found = 0

if xml_data:
    try:
        root = ET.fromstring(xml_data)
        channel = root.find("channel")
        items = channel.findall("item")

        for item in items[:15]:
            title = item.findtext("title")
            link = item.findtext("link")
            description = item.findtext("description")
            pub_date = item.findtext("pubDate")

            # Übersetzen
            title_de = translate_to_german(title)
            description_de = translate_to_german(description)

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title_de)
            fe.link(href=link)
            fe.description(description_de)
            fe.pubDate(pub_date)

            articles_found += 1

        print(f"{articles_found} Artikel erfolgreich übernommen und übersetzt.")

    except Exception as e:
        print(f"Fehler beim Verarbeiten des XML: {e}")

# 5. Fallback
if articles_found == 0:
    fe = fg.add_entry()
    fe.id("https://home.cern/news/fallback")
    fe.title("CERN Feed wartet auf Updates")
    fe.link(href="https://home.cern/news")
    fe.description("Der Feed ist aktiv, aber der CERN-Feed lieferte keine Artikel.")
    fe.pubDate(datetime.now(timezone.utc))

# 6. RSS-Datei schreiben
fg.rss_file('public/cern_feed.xml', pretty=True)
print("Feed-Datei erfolgreich aktualisiert.")
