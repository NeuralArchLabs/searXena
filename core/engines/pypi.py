from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://pypi.org/search/?{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('a.package-snippet'):
        title_node = node.css_first('span.package-snippet__name')
        version_node = node.css_first('span.package-snippet__version')
        desc_node = node.css_first('p.package-snippet__description')
        
        if title_node:
            name = title_node.text().strip()
            version = version_node.text().strip() if version_node else ""
            results.append({
                "title": f"PyPI: {name} {version}",
                "url": "https://pypi.org" + node.attributes.get('href', ''),
                "content": desc_node.text().strip() if desc_node else "Paquete de Python.",
                "source": "pypi"
            })
    return results
