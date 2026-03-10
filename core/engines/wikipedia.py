from urllib.parse import urlencode

NAME = "wikipedia"
CATEGORIES = ['general', 'it', 'science']
WEIGHT = 3.0

def request(query, params):
    lang = params.get("language", "es")
    query_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|info|pageimages",
        "exintro": True,
        "explaintext": True,
        "exsentences": 3,
        "inprop": "url",
        "pithumbsize": 400,
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 3
    }
    params["url"] = f"https://{lang}.wikipedia.org/w/api.php?{urlencode(query_params)}"
    params["headers"]["User-Agent"] = "searXena/1.0 (https://github.com/martinezpalomera92/searXena; contact: user@example.com) modern-browser-style"

def response(resp):
    results = []
    try:
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if "extract" in page:
                results.append({
                    "title": page.get("title", ""),
                    "url": page.get("fullurl", f"https://wikipedia.org/?curid={page_id}"),
                    "content": page.get("extract", ""),
                    "img_src": page.get("thumbnail", {}).get("source") if "thumbnail" in page else None,
                    "template": "infobox.html", # Promocionar a Infobox
                    "source": "wikipedia"
                })
    except Exception:
        pass
    return results
