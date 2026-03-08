from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

CATEGORIES = ["videos"]

def request(query, params):
    params["url"] = f"https://vimeo.com/search?{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Vimeo usa un layout moderno con componentes JS, pero suele dejar migas en el HTML
    for node in tree.css('a[href^="/"], div[class^="iris_video_item"]'):
        title_node = node.css_first('span[class*="title"], h3')
        if title_node:
            url = "https://vimeo.com" + node.attributes.get('href', '')
            results.append({
                "title": title_node.text().strip(),
                "url": url,
                "content": "Video en Vimeo.",
                "score": 1.0
            })
    return results
