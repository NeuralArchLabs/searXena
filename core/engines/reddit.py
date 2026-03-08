from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general", "social"]

def request(query, params):
    # Usar Reddit search (version light/old para mejor scraping)
    query_params = {
        "q": query,
        "source": "recent",
        "type": "link"
    }
    params["url"] = f"https://www.reddit.com/search?{urlencode(query_params)}"
    params["headers"]["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div[data-testid="post-container"], faceplate-batch article'):
        title_node = node.css_first('a[data-testid="post-title"], h2')
        url_node = node.css_first('a[data-testid="post-title"]')
        
        if title_node:
            url = url_node.attributes.get('href', '') if url_node else ""
            if url and not url.startswith('http'):
                url = "https://www.reddit.com" + url
                
            results.append({
                "title": title_node.text().strip(),
                "url": url,
                "content": "Conversación en Reddit sobre este tema."
            })
    return results
