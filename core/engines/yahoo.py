from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

def request(query, params):
    query_params = {'p': query}
    if params.get('pageno', 1) > 1:
        query_params['b'] = (params['pageno'] - 1) * 10 + 1
        
    params["url"] = f"https://search.yahoo.com/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.algo-sr'):
        title_node = node.css_first('h3 a')
        snippet_node = node.css_first('div.compText')
        
        if title_node:
            url = title_node.attributes.get('href', '')
            # Limpiar redirecciones de Yahoo
            if '/RU=' in url:
                try:
                    url = unquote(url.split('/RU=')[1].split('/RK=')[0])
                except:
                    pass
            
            results.append({
                "title": title_node.text().strip(),
                "url": url,
                "content": snippet_node.text().strip() if snippet_node else ""
            })
    return results
