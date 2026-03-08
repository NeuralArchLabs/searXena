import httpx
from urllib.parse import urlencode

CATEGORIES = ["it", "general"]

def request(query, params):
    # Usar Algolia API para HackerNews
    query_params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": 5
    }
    params["url"] = f"https://hn.algolia.com/api/v1/search?{urlencode(query_params)}"

def response(resp):
    results = []
    try:
        data = resp.json()
        for hit in data.get("hits", []):
            url = hit.get("url")
            if not url:
                url = f"https://news.ycombinator.com/item?id={hit['objectID']}"
            
            results.append({
                "title": hit.get("title", ""),
                "url": url,
                "content": f"Points: {hit.get('points')} | Author: {hit.get('author')}",
                "score": 1.5 # HackerNews results are high quality for IT
            })
    except:
        pass
    return results
