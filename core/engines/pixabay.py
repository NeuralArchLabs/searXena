from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["images", "videos"]

def request(query, params):
    category = params.get("category", "images")
    pageno = params.get("pageno", 1)
    
    if category == "videos":
        params["url"] = f"https://pixabay.com/videos/search/{query}/?pagi={pageno}"
    else:
        params["url"] = f"https://pixabay.com/images/search/{query}/?pagi={pageno}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Imagenes
    if "/images/" in resp.url or "images" in resp.search_params.get("category", ""):
        for node in tree.css('div.cell--i699w img, div.container--S686f img'):
            src = node.attributes.get('src') or node.attributes.get('data-lazy')
            if src and "static" in src:
                results.append({
                    "template": "images.html",
                    "title": node.attributes.get('alt', 'Pixabay Image'),
                    "url": src,
                    "img_src": src,
                    "thumbnail_src": src,
                    "content": "Imagen gratuita de Pixabay"
                })
    
    # Videos
    if "/videos/" in resp.url or "videos" in resp.search_params.get("category", ""):
        for node in tree.css('div.container--S686f a[href*="/videos/"]'):
            title_node = node.css_first('div.description--P26Xv, span')
            img_node = node.css_first('img')
            if title_node:
                results.append({
                    "template": "videos.html",
                    "title": title_node.text().strip(),
                    "url": "https://pixabay.com" + node.attributes.get('href', ''),
                    "img_src": img_node.attributes.get('src') if img_node else None,
                    "content": "Video gratuito de Pixabay"
                })
            
    return results
