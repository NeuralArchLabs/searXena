import httpx
from urllib.parse import urlencode

CATEGORIES = ["general", "it"]

def request(query, params):
    query_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|info",
        "exintro": True,
        "explaintext": True,
        "exsentences": 3,
        "inprop": "url",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 3
    }
    params["url"] = f"https://en.wikipedia.org/w/api.php?{urlencode(query_params)}"

def response(resp):
    results = []
    try:
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if "extract" in page:
                results.append({
                    "title": page.get("title", ""),
                    "url": page.get("fullurl", f"https://en.wikipedia.org/?curid={page_id}"),
                    "content": page.get("extract", ""),
                    "score": 2.5 # Wikipedia siempre arriba en IT/General
                })
    except:
        pass
    return results
