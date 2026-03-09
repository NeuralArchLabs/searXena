from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "p": query,
        "b": (params.get("pageno", 1) - 1) * 10 + 1
    }
    params["url"] = f"https://search.yahoo.com/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.dd.algo'):
        title_node = node.css_first('h3 a')
        snippet_node = node.css_first('div.compText, span.fc-recos')
        
        if title_node:
            url = title_node.attributes.get('href', '')
            # Yahoo suele usar redirecciones
            if "r.search.yahoo.com" in url:
                try:
                    # Intento de limpieza rapida
                    url = unquote(url.split('/RU=')[1].split('/RK=')[0])
                except: pass
                
            results.append({
                "title": title_node.text().strip(),
                "url": url,
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "yahoo"
            })
    return results
