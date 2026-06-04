import os
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# 1. Ordner sofort erstellen (behebt den Tar-Fehler)
os.makedirs('public', exist_ok=True)

api_url = "https://home.cern/api/news?page=0&items_per_page=15"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print("Rufe CERN-API ab...")
try:
    response = requests.get(api_url, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    print("API-Abruf erfolgreich.")
except Exception as e:
    print(f"Fehler beim API-Abruf: {e}")
    # Erstelle leeren Feed als Fallback, damit die Action nicht abstürzt
    data = {"nodes": []}

# 2. Feed initialisieren
fg = FeedGenerator()
fg.id('https://home.cern/news')
fg.title('CERN News - Inoffizieller Feed')
fg.link(href='https://home.cern/news', rel='alternate')
fg.description('Die neuesten Meldungen direkt von der CERN-Hauptseite via API')
fg.language('en')

# 3. Artikel verarbeiten
articles = data.get('nodes', []) if isinstance(data, dict) else data
articles_found = 0

for item in articles:
    node = item.get('node', item) if isinstance(item, dict) else {}
    title = node.get('title')
    path = node.get('path') or node.get('url')
    summary = node.get('body') or node.get('summary') or f"CERN Update: {title}"
    
    if not title or not path:
        continue
        
    full_url = "https://home.cern" + path if path.startswith('/') else path
    
    fe = fg.add_entry()
    fe.id(full_url)
    fe.title(title)
    fe.link(href=full_url)
    fe.summary(summary)
    fe.updated(datetime.now(timezone.utc))
    articles_found += 1

# 4. Datei schreiben
fg.atom_file('public/cern_feed.xml', pretty=True)
print(f"Fertig! {articles_found} Artikel in public/cern_feed.xml gespeichert.")
