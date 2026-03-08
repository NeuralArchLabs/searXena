from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["it"]

def request(query, params):
    params["url"] = f"https://www.npmjs.com/search?{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.npm-search-results > div, section div[class*="v-mid"]'):
        title_node = node.css_first('h3, a[href^="/package/"] h3')
        url_node = node.css_first('a[href^="/package/"]')
        snippet_node = node.css_first('p')
        
        if title_node and url_node:
            results.append({
                "title": f"NPM: {title_node.text().strip()}",
                "url": "https://www.npmjs.com" + url_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "JS package.",
                "score": 1.1
            })
    return results
