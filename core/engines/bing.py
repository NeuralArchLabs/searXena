from selectolax.parser import HTMLParser
from urllib.parse import urlencode, urlparse, parse_qs
import base64

def request(query, params):
    # Cookies mágicas de Bing para evitar bloqueos y fijar el mercado
    params["cookies"]["_EDGE_CD"] = "m=us&u=en"
    params["cookies"]["_EDGE_S"] = "mkt=en-us&ui=en"
    
    query_params = {
        "q": query,
        "pq": query,
        "FORM": "QBRE"
    }
    
    if params.get("pageno", 1) > 1:
        query_params["first"] = (params["pageno"] - 1) * 10 + 1
        query_params["FORM"] = f"PERE{(params['pageno']-2) if params['pageno'] > 2 else ''}"

    params["url"] = f"https://www.bing.com/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('ol#b_results li.b_algo'):
        title_tag = node.css_first('h2 a')
        snippet_tag = node.css_first('p, div.b_caption p')
        
        if title_tag:
            url = title_tag.attributes.get('href', '')
            
            # Bing a veces usa redirecciones base64 en /ck/a?
            if url.startswith('https://www.bing.com/ck/a?'):
                url_query = urlparse(url).query
                parsed = parse_qs(url_query)
                if 'u' in parsed:
                    v = parsed['u'][0][2:] # quitar a1
                    v = v + "=" * (-len(v) % 4) # padding
                    url = base64.urlsafe_b64decode(v).decode('utf-8')

            results.append({
                "title": title_tag.text().strip(),
                "url": url,
                "content": snippet_tag.text().strip() if snippet_tag else ""
            })
    return results
