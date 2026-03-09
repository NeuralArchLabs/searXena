from selectolax.parser import HTMLParser
from urllib.parse import urlencode

NAME = "ebay"
CATEGORIES = ["shopping"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://www.ebay.com/sch/i.html?_nkw={query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li.s-item'):
        title_node = node.css_first('div.s-item__title')
        link_node = node.css_first('a.s-item__link')
        price_node = node.css_first('span.s-item__price')
        
        if title_node and link_node:
            results.append({
                "title": f"eBay: {title_node.text().strip()}",
                "url": link_node.attributes.get('href', ''),
                "content": f"Precio: {price_node.text().strip()}" if price_node else "Producto en eBay.",
                "source": "ebay"
            })
    return results
