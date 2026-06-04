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
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

articles_found = 0

try:
    print("Rufe CERN News-Webseite ab...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    html = response.text

    # Verbessertes Suchmuster: Findet alle Links, die mit /news/ oder /opinion/ beginnen
    matches = re.findall(r'href=\"((?:/news/|/opinion/)[^\"]+)\"[^>]*>(.*?)</a>', html)
    
    seen_urls = set()
    for path, title in matches:
        # Bereinige den Titel von HTML-Resten und Leerzeichen
        title = re.sub('<[^<]+?>', '', title).strip()
        
        # Ignoriere zu kurze Texte (wie "News" oder "Read more")
        if not title or len(title) < 15 or path in seen_urls:
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
        
        if articles_found >= 15:
            break

    print(f"Webseite erfolgreich ausgelesen. {articles_found} echte Artikel gefunden.")
except Exception as e:
    print(f"Fehler beim Auslesen der Webseite: {e}")

# Falls wirklich gar nichts gefunden wurde, greift der Fallback
if articles_found == 0:
    fe = fg.add_entry()
    fe.id("https://home.cern/news/fallback")
    fe.title("CERN News Feed wartet auf Updates")
    fe.link(href="https://home.cern/news")
    fe.summary("Der Feed ist aktiv, sucht aber noch nach dem richtigen Artikelformat.")
    fe.updated(datetime.now(timezone.utc))

# 4. Datei schreiben (JETZT ALS RSS)
fg.rss_file('public/cern_feed.xml', pretty=True)
print("Feed-Datei erfolgreich aktualisiert.")
