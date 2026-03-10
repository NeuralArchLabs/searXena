from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

CATEGORIES = ["videos"]
WEIGHT = 2.0

def request(query, params):
    start = (params.get("pageno", 1) - 1) * 10
    query_params = {
        "q": query,
        "tbm": "vid",
        "start": start,
        "hl": "es",
        "gl": "ES"
    }
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # En Google Videos, los resultados suelen estar en bloques div.g
    for node in tree.css('div.MjjYud, div.g'):
        title_node = node.css_first('h3')
        url_node = node.css_first('a')
        img_node = node.css_first('img')
        snippet_node = node.css_first('div.VwiC3b')
        
        if title_node and url_node:
            url = url_node.attributes.get('href', '')
            if url.startswith('/url?q='):
                url = unquote(url[7:].split('&sa=')[0])
                
            if url.startswith('http') and not "google.com" in url:
                img_src = img_node.attributes.get('src') or img_node.attributes.get('data-src') if img_node else None
                
                # Try to get high quality youtube thumbnails directly
                if "youtube.com/watch?v=" in url:
                    try:
                        v_id = url.split("v=")[1].split("&")[0]
                        img_src = f"https://img.youtube.com/vi/{v_id}/mqdefault.jpg"
                    except Exception:
                        pass
                
                results.append({
                    "template": "videos.html",
                    "title": title_node.text().strip(),
                    "url": url,
                    "img_src": img_src,
                    "content": snippet_node.text().strip() if snippet_node else "Video de Google.",
                    "source": "google_videos"
                })
    return results
