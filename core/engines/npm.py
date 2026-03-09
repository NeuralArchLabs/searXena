from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://www.npmjs.com/search?{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div._356262b9'):
        title_node = node.css_first('h3')
        desc_node = node.css_first('p')
        url_node = node.css_first('a')
        
        if title_node and url_node:
            results.append({
                "title": f"NPM: {title_node.text().strip()}",
                "url": "https://www.npmjs.com" + url_node.attributes.get('href', ''),
                "content": desc_node.text().strip() if desc_node else "Paquete de Node.js.",
                "source": "npm"
            })
    return results
