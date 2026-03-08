from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

CATEGORIES = ["news"]

def request(query, params):
    # Google News modo móvil (siempre devuelve HTML simple y rico)
    query_params = {
        "q": query,
        "tbm": "nws",
        "hl": "es",
        "gl": "ES",
        "start": (params.get("pageno", 1) - 1) * 10
    }
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"
    params["headers"]["User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # En móvil, las noticias suelen ir en selectores 'div[role="heading"]' o dentro de bloques 'a'
    for node in tree.css('a[href*="url?q="]'):
        title_node = node.css_first('div[role="heading"]')
        snippet_node = node.css_first('div.S5uMzb, div.BNeawe.s31JSe, div.BNeawe.tAd7D')
        
        if title_node:
            url = node.attributes.get('href', '')
            if '/url?q=' in url:
                url = unquote(url.split('/url?q=')[1].split('&sa=')[0])
                
            if url.startswith('http') and "google.com" not in url:
                results.append({
                    "title": title_node.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "Noticia móvil detectada."
                })
                
    return results
