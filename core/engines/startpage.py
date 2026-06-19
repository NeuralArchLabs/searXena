from selectolax.parser import HTMLParser
from urllib.parse import urlencode
from utils import LANGUAGE_MAP

CATEGORIES = ["general"]
WEIGHT = 3.0

def request(query, params):
    # Startpage requires POST for search recently to prevent basic scraping
    lang = params.get("language", "es")
    sp_lang = LANGUAGE_MAP.get("startpage", {}).get(lang, "english")
    
    query_params = {
        "query": query,
        "cat": "web",
        "cmd": "process_search",
        "language": sp_lang,
        "engine0": "v1all",
        "t": "device",
        "abp": "-1",
        "pg": params.get("pageno", 1),
    }
    params["url"] = "https://www.startpage.com/sp/search"
    params["method"] = "POST"
    params["data"] = query_params
    params["headers"]["Referer"] = "https://www.startpage.com/"
    params["headers"]["Origin"] = "https://www.startpage.com"
    params["headers"]["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    params["headers"]["Accept-Encoding"] = "gzip, deflate"
    params["cookies"]["preferences"] = "language_ui=english&search_engine=google&results_per_page=20"
    params["cookies"]["post_parameters"] = "1"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)

    # Selectores modernos y fallback
    for node in tree.css('div.result, article.result, .w-gl__result'):
        title_link = node.css_first('a.w-gl__result-title, a.result-link, a.result-title, h2 a, h3 a')
        snippet_node = node.css_first('p.w-gl__result-description, p.description, .result-snippet, .description')

        if title_link:
            url = title_link.attributes.get('href', '')
            if url and url.startswith('http') and "startpage.com" not in url:
                results.append({
                    "title": title_link.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "",
                    "source": "startpage"
                })
    return results
