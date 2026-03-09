from selectolax.parser import HTMLParser

CATEGORIES = ["general", "news"]
WEIGHT = 2.2

def request(query, params):
    # Brave Search
    offset = (params.get("pageno", 1) - 1) * 20
    params["url"] = f"https://search.brave.com/search?q={query}&offset={offset}"
    params["headers"]["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.snippet'):
        title_link = node.css_first('a.search-result_link, a[href^="http"]')
        title_text = node.css_first('span.name, h2, .title')
        snippet_node = node.css_first('.snippet-description, .result-content, .description')
        
        if title_link:
            url = title_link.attributes.get('href', '')
            # Evitar enlaces internos de brave
            if url and "brave.com" not in url and url.startswith('http'):
                results.append({
                    "title": title_text.text().strip() if title_text else title_link.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "Información de Brave Search.",
                    "source": "brave"
                })
    return results
