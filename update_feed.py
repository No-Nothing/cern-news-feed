import os
import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# 1. Ordner sofort erstellen
os.makedirs('public', exist_ok=True)

# 2. Feed initialisieren
fg = FeedGenerator()
fg.id('https://home.cern/news')
fg.title('CERN News - Inoffizieller Feed')
fg.link(href='https://home.cern/news', rel='alternate')
fg.description('Die neuesten Meldungen direkt von der CERN-Hauptseite')
fg.language('en')

# 3. Direkt die News-Webseite abrufen
url = "https://home.cern/news"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

articles_found = 0

try:
    print("Rufe CERN News-Webseite ab...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    html = response.text

    # Wir suchen nach Links und Titeln im HTML-Code mittels regulärer Ausdrücke
    matches = re.findall(r'<a\s+href="(/news/[^"]+)"[^>]*>(.*?)</a>', html)
    
    seen_urls = set()
    for path, title in matches:
        title = re.sub('<[^<]+?>', '', title).strip() # HTML-Tags aus Titel entfernen
        if not title or len(title) < 10 or path in seen_urls:
            continue
            
        seen_urls.add(path)
        full_url = "https://home.cern" + path
        
        fe = fg.add_entry()
        fe.id(full_url)
        fe.title(title)
        fe.link(href=full_url)
        fe.summary(f"Read the full article on CERN News: {title}")
        fe.updated(datetime.now(timezone.utc))
        articles_found += 1
        
        if articles_found >= 15: # Begrenzen auf die 15 neuesten
            break

    print(f"Webseite erfolgreich ausgelesen. {articles_found} Artikel gefunden.")
except Exception as e:
    print(f"Fehler beim Auslesen der Webseite: {e}")

# Falls gar nichts gefunden wurde, einen Dummy-Artikel einfügen
if articles_found == 0:
    fe = fg.add_entry()
    fe.id("https://home.cern/news/fallback")
    fe.title("CERN News Feed ist aktiv")
    fe.link(href="https://home.cern/news")
    fe.summary("Der Feed wurde erfolgreich eingerichtet und wartet auf neue Artikel.")
    fe.updated(datetime.now(timezone.utc))

# 4. Datei schreiben
fg.atom_file('public/cern_feed.xml', pretty=True)
print("Feed-Datei erfolgreich aktualisiert.")
