STATUS = "experimental"
from selectolax.parser import HTMLParser
from urllib.parse import urlencode, urlparse, parse_qs, unquote
import base64

CATEGORIES = ["general", "news"]
WEIGHT = 3.0

def request(query, params):
    # Cookies to force English market and avoid redirects
    params["cookies"]["_EDGE_CD"] = "m=en-us&u=en-us"
    params["cookies"]["_EDGE_S"] = "mkt=en-us&ui=en-us"
    params["cookies"]["MUID"] = ""
    params["cookies"]["SRCHD"] = "AF=NOFORM"
    params["cookies"]["SRCHUSR"] = "DOB=20200101"
    
    query_params = {
        "q": query,
        "pq": query,
        "FORM": "QBRE",
        "cc": "us",
        "setlang": "en",
    }
    
    if params.get("pageno", 1) > 1:
        query_params["first"] = (params["pageno"] - 1) * 10 + 1
        query_params["FORM"] = f"PERE{(params['pageno']-2) if params['pageno'] > 2 else ''}"

    params["url"] = f"https://www.bing.com/search?{urlencode(query_params)}"
    params["headers"]["Accept-Language"] = "en-US,en;q=0.9"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Updated selectors: more generic
    for node in tree.css('li.b_algo, .b_algo, div#b_results li, article'):
        title_tag = node.css_first('h2 a, h3 a, .title a, a')
        snippet_tag = node.css_first('div.b_caption p, .b_caption p, div.b_snippet, p')
        
        if title_tag:
            url = title_tag.attributes.get('href', '')
            
            # Bing sometimes wraps URLs in /ck/a? redirects with base64
            if url.startswith('https://www.bing.com/ck/a?'):
                url = _decode_bing_url(url)
            
            if url and url.startswith('http') and 'bing.com' not in url:
                results.append({
                    "title": title_tag.text().strip(),
                    "url": url,
                    "content": snippet_tag.text().strip() if snippet_tag else "Resultado de Bing.",
                    "source": "bing"
                })
    return results

def _decode_bing_url(url):
    """Decode Bing's base64 wrapped redirect URLs."""
    try:
        url_query = urlparse(url).query
        parsed = parse_qs(url_query)
        if 'u' in parsed:
            v = parsed['u'][0]
            if v.startswith('a1'):
                v = v[2:]  # Remove 'a1' prefix
            v = v + "=" * (-len(v) % 4)  # Add padding
            decoded = base64.urlsafe_b64decode(v).decode('utf-8')
            return decoded
    except:
        pass
    return url
