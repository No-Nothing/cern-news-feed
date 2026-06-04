import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# 1. Ordner erstellen
os.makedirs('public', exist_ok=True)

# 2. Feed initialisieren
fg = FeedGenerator()
fg.id('https://home.cern/news')
fg.title('CERN News - Inoffizieller Feed')
fg.link(href='https://home.cern/news', rel='alternate')
fg.description('Die neuesten Meldungen direkt von der CERN-Hauptseite')
fg.language('en')

url = "https://home.cern/news"
headers = {"User-Agent": "Mozilla/5.0"}

articles_found = 0

try:
    print("Rufe CERN News-Webseite ab...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Alle möglichen Artikel-Container
    candidates = soup.select("a.card__link, a.teaser__link, a[href^='/news/'], a[href^='/opinion/']")

    seen = set()

    for a in candidates:
        href = a.get("href")
        if not href or not href.startswith(("/news/", "/opinion/")):
            continue

        if href in seen:
            continue
        seen.add(href)

        # Titel extrahieren
        title = a.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        full_url = "https://home.cern" + href

        # Artikel-Datum extrahieren (falls vorhanden)
        date_tag = a.find_parent().find("time")
        if date_tag and date_tag.get("datetime"):
            try:
                pub_date = datetime.fromisoformat(date_tag["datetime"].replace("Z", "+00:00"))
            except:
                pub_date = datetime.now(timezone.utc)
        else:
            pub_date = datetime.now(timezone.utc)

        # Feed-Eintrag
        fe = fg.add_entry()
        fe.id(full_url)
        fe.title(title)
        fe.link(href=full_url)
        fe.published(pub_date)
        fe.summary(f"Read the full article on CERN News: {title}")

        articles_found += 1
        if articles_found >= 15:
            break

    print(f"{articles_found} Artikel gefunden.")

except Exception as e:
    print(f"Fehler beim Auslesen: {e}")

# Fallback, falls nichts gefunden wurde
if articles_found == 0:
    fe = fg.add_entry()
    fe.id("https://home.cern/news/fallback")
    fe.title("CERN News Feed wartet auf Updates")
    fe.link(href="https://home.cern/news")
    fe.summary("Der Feed ist aktiv, sucht aber noch nach dem richtigen Artikelformat.")
    fe.updated(datetime.now(timezone.utc))

# 4. RSS-Datei schreiben
fg.rss_file('public/cern_feed.xml', pretty=True)
print("Feed-Datei erfolgreich aktualisiert.")
