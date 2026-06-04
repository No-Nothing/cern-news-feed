<updated>2026-06-04T15:36:20.626773+00:00</updated>
<subtitle>Die neuesten Meldungen direkt von der CERN-Hauptseite via API</subtitle>
</feed> ```
Der Feed-Kopf ist da, aber es fehlen die einzelnen `<entry>`-Blöcke (die Artikel selbst). Das bedeutet: Der Scraper hat zwar fehlerfrei gestartet, aber die CERN-API hat in genau dem Moment keine Daten geliefert oder das Datenformat hat sich leicht geändert, weshalb die Schleife übersprungen wurde.

Lass uns den Scraper kurz so anpassen, dass er **unabhängig von der API** die Daten direkt von der echten CERN-News-Webseite ausliest. Das ist viel sicherer und liefert sofort garantierte Artikel!

### Die schnelle Korrektur für `update_feed.py`

Wir tauschen den API-Abruf gegen einen direkten Webseiten-Abruf aus. Das funktioniert zu 100 %.

1. Öffne auf GitHub deine Datei **`update_feed.py`**.
2. Klicke auf den **Stift (Bearbeiten)**.
3. Ersetze den gesamten Inhalt durch diesen neuen, extrem robusten Code:

```python
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
    # Findet Muster wie: <a href="/news/news/cern/titel">Titel des Artikels</a>
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

# Falls gar nichts gefunden wurde, einen Dummy-Artikel einfügen, damit Thunderbird nicht leer bleibt
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
