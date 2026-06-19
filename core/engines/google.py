STATUS = "experimental"
import random
from urllib.parse import urlencode, unquote
from utils import LANGUAGE_MAP
from selectolax.parser import HTMLParser

CATEGORIES = ["general", "news", "videos", "images"]
WEIGHT = 1.5

# Mobile UAs bypass Google's JS-only anti-bot page
_MOBILE_UAS = [
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.0.0 Mobile/15E148 Safari/604.1",
]

def request(query, params):
    offset = (params.get("pageno", 1) - 1) * 10
    lang = params.get("language", "es")
    lang_code = LANGUAGE_MAP.get("google", {}).get(lang, "es")
    category = params.get("category", "general")

    query_params = {"q": query, "hl": lang_code, "start": offset}

    if category == "news":
        query_params["tbm"] = "nws"
    elif category == "videos":
        query_params["tbm"] = "vid"
    elif category == "images":
        query_params["tbm"] = "isch"

    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"
    params["headers"]["User-Agent"] = random.choice(_MOBILE_UAS)
    params["headers"]["Accept-Encoding"] = "gzip, deflate"
    params["headers"]["Referer"] = "https://www.google.com/"

    cb_val = random.randint(20230000, 20249999)
    params["cookies"]["CONSENT"] = f"YES+cb.{cb_val}-04-p0.{lang}+FX+414"
    params["cookies"]["SOCS"] = "CAESHAgBEhJmb3NfbGVzcy9zZWFyY2gvaG9tZQ"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)

    # Mobile Google layout uses these selectors
    # .BVG0Nb = container, .DKV0Md = title, .iCjJK = snippet (mobile)
    # Standard: div.g, div.MjjYud, h3.LC20lb, div.VwiC3b
    selectors = [
        ('div.MjjYud', 'h3.LC20lb, h3, .DKV0Md', 'div.VwiC3b, .iCjJK, .BNeawe'),
        ('div.g', 'h3', 'div.VwiC3b, span.st, p'),
        ('.Gx5S9b', 'h3, .vv14be', '.BNeawe, .s3v9rd'),
        ('.kp-blk', 'h3', 'p'),
    ]

    for container_sel, title_sel, snippet_sel in selectors:
        for node in tree.css(container_sel):
            title_node = node.css_first(title_sel)
            url_node = node.css_first('a[href]')
            snippet_node = node.css_first(snippet_sel)

            if title_node and url_node:
                url = _clean_url(url_node.attributes.get('href', ''))
                if _valid_url(url):
                    title = title_node.text().strip()
                    if title and len(title) > 3:
                        results.append({
                            "title": title,
                            "url": url,
                            "content": snippet_node.text().strip() if snippet_node else "",
                            "source": "google"
                        })
        if results:
            break

    # Fallback: any h3 in a link
    if not results:
        for node in tree.css('h3'):
            link = node.parent
            limit = 5
            while link and link.tag != 'a' and limit > 0:
                link = link.parent
                limit -= 1
            if link and link.tag == 'a':
                url = _clean_url(link.attributes.get('href', ''))
                if _valid_url(url):
                    title = node.text().strip()
                    if title:
                        results.append({
                            "title": title,
                            "url": url,
                            "content": "",
                            "source": "google"
                        })

    # Images (isch)
    if "tbm=isch" in getattr(resp, 'url', ''):
        for node in tree.css('div.isv-r, .isv-r, .oj9v4c'):
            img_node = node.css_first('img')
            link_node = node.css_first('a[href^="http"]')
            if img_node:
                src = img_node.attributes.get('src') or img_node.attributes.get('data-src')
                if src:
                    results.append({
                        "template": "images.html",
                        "title": "Imagen de Google",
                        "url": link_node.attributes.get('href', '#') if link_node else "#",
                        "img_src": src,
                        "source": "google"
                    })

    return results

def _clean_url(url):
    """Clean Google redirect URLs."""
    if url.startswith('/url?q='):
        url = unquote(url[7:].split('&sa=')[0])
    if '/url?esrc=' in url:
        try:
            url = unquote(url.split('url=')[1].split('&')[0])
        except:
            pass
    return url

def _valid_url(url):
    """Check if URL is a valid external result."""
    return (url.startswith('http') and
            "google.com" not in url and
            "google." not in url[:22] and
            len(url) > 10)
