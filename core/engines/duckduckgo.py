from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote
from utils import LANGUAGE_MAP

CATEGORIES = ["general"]
WEIGHT = 1.8

def request(query, params):
    # DDG HTML version - POST request to bypass bot block/captcha
    lang = params.get("language", "es")
    kl = LANGUAGE_MAP.get("duckduckgo", {}).get(lang, "wt-wt")
    
    params["url"] = "https://html.duckduckgo.com/html/"
    params["method"] = "POST"
    params["data"] = {
        "q": query,
        "kl": kl,
        "b": ""
    }
    params["headers"]["Referer"] = "https://html.duckduckgo.com/"
    params["headers"]["Accept-Language"] = f"{lang},en;q=0.8"
    params["headers"]["Origin"] = "https://html.duckduckgo.com"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # DDG HTML version: results are in div.result
    for node in tree.css('div.result'):
        title_node = node.css_first('a.result__a') or node.css_first('.result__title a')
        snippet_node = node.css_first('.result__snippet')
        
        if title_node:
            title = title_node.text().strip()
            url = title_node.attributes.get('href', '')
            
            if 'uddg=' in url:
                try:
                    url = unquote(url.split('uddg=')[1].split('&')[0])
                except:
                    pass
            
            if url.startswith('http') and not "duckduckgo.com" in url:
                content = snippet_node.text().strip() if snippet_node else "Información de DuckDuckGo."
                results.append({
                    "title": title,
                    "url": url,
                    "content": content,
                    "source": "duckduckgo"
                })
    return results
