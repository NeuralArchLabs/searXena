from selectolax.parser import HTMLParser
from urllib.parse import urlencode

NAME = "brave_news"
CATEGORIES = ["news"]
WEIGHT = 1.5

def request(query, params):
    params["url"] = f"https://search.brave.com/news?q={query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Brave News usa selectores específicos para artículos
    for node in tree.css('div.news-item, div.card'):
        title_node = node.css_first('a.title, .heading-sm')
        snippet_node = node.css_first('.news-description, .snippet-description, p')
        source_node = node.css_first('.news-source, .source')
        
        if title_node:
            url = title_node.attributes.get('href', '')
            if url and url.startswith('http'):
                results.append({
                    "title": title_node.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "Noticia vía Brave News.",
                    "source": source_node.text().strip() if source_node else "brave_news"
                })
    return results
