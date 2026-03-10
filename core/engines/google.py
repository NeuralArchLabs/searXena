STATUS = "experimental"
import random
from urllib.parse import urlencode, unquote
from selectolax.parser import HTMLParser

CATEGORIES = ["general", "news", "videos", "images"]
WEIGHT = 1.5

def request(query, params):
    # Google with udm=14 (clean Web view, less bot detection)
    offset = (params.get("pageno", 1) - 1) * 10
    
    query_params = {
        "q": query,
        "hl": params.get("language", "es"),
        "start": offset,
        "udm": 14, # New Web search view
    }
    
    if params.get("category") == "news":
        query_params["tbm"] = "nws"
        query_params.pop("udm", None)
    elif params.get("category") == "videos":
        query_params["tbm"] = "vid"
        query_params.pop("udm", None)
    elif params.get("category") == "images":
        query_params["tbm"] = "isch"
        query_params.pop("udm", None)
        
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"
    params["headers"]["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    params["headers"]["Referer"] = "https://www.google.com/"
    
    # Consent cookies to bypass 'Before you continue'
    params["cookies"]["CONSENT"] = "YES+"
    params["cookies"]["SOCS"] = "CAISHAgBEhJnd3NfMjAyNDA0MTYtMF9SQzIaAnp6IAEaBgiA_LGsBg"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Common selectors for Google Web (udm=14 and standard)
    for node in tree.css('div.g, .MjjYud, .g, div.ZIN69b, .WwS1ce'):
        title_node = node.css_first('h3')
        url_node = node.css_first('a[href]')
        # Snippet can be in several places
        snippet_node = node.css_first('div.VwiC3b, .VwiC3b, .BNeawe, .s3v9rd, span.st')
        
        if title_node and url_node:
            url = _clean_url(url_node.attributes.get('href', ''))
            if _valid_url(url):
                title = title_node.text().strip()
                if title:
                    results.append({
                        "title": title,
                        "url": url,
                        "content": snippet_node.text().strip() if snippet_node else "Información de Google.",
                        "source": "google"
                    })
    
    # Fallback to any h3 link
    if not results:
        for node in tree.css('h3'):
            link = node.parent
            while link and link.tag != 'a':
                link = link.parent
            
            if link:
                url = _clean_url(link.attributes.get('href', ''))
                if _valid_url(url):
                    results.append({
                        "title": node.text().strip(),
                        "url": url,
                        "content": "Ver en Google.",
                        "source": "google"
                    })

    # Images (isch)
    if "tbm=isch" in resp.url:
        for node in tree.css('div.isv-r, .isv-r'):
            img_node = node.css_first('img')
            link_node = node.css_first('a[href^="http"]')
            if img_node:
                src = img_node.attributes.get('src') or img_node.attributes.get('data-src')
                if src:
                    results.append({
                        "template": "images.html",
                        "title": "Imagen de Google",
                        "url": link_node.attributes.get('href', '#') if link_node else "#",
                        "img_src": src,
                        "source": "google"
                    })

    return results

def _clean_url(url):
    """Clean Google redirect URLs."""
    if url.startswith('/url?q='):
        url = unquote(url[7:].split('&sa=')[0])
    if '/url?esrc=' in url:
        try:
            url = unquote(url.split('url=')[1].split('&')[0])
        except:
            pass
    return url

def _valid_url(url):
    """Check if URL is a valid external result."""
    return url.startswith('http') and "google.com" not in url
