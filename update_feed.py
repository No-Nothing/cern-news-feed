import os
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

def generate_cern_feed():
    api_url = "https://home.cern/api/news?page=0&items_per_page=15"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Fehler beim Abrufen der CERN-API: {e}")
        return

    fg = FeedGenerator()
    fg.id('https://home.cern/news')
    fg.title('CERN News - Inoffizieller Feed')
    fg.link(href='https://home.cern/news', rel='alternate')
    fg.description('Die neuesten Meldungen direkt von der CERN-Hauptseite via API')
    fg.language('en')

    articles_found = 0
    articles = data.get('nodes', []) if isinstance(data, dict) else data
    
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

    os.makedirs('public', exist_ok=True)
    fg.atom_file('public/cern_feed.xml', pretty=True)
    print(f"Erfolgreich: {articles_found} Artikel via API im Feed gespeichert.")

if __name__ == "__main__":
    generate_cern_feed()
