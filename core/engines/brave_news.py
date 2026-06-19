from selectolax.parser import HTMLParser

CATEGORIES = ["news"]
WEIGHT = 1.5

def request(query, params):
    offset = (params.get("pageno", 1) - 1) * 20
    lang = params.get("language", "es")
    params["url"] = f"https://search.brave.com/news?q={query}&offset={offset}&hl={lang}"
    params["headers"]["Accept-Encoding"] = "gzip, deflate"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.snippet'):
        title_link = node.css_first('a.l1, a[href^="http"]')
        title_node = node.css_first('.title')
        snippet_node = node.css_first('.description, .content, p')
        
        # Extraer fuente o tiempo si lo hay
        source_node = node.css_first('.netloc, .source')
        time_node = node.css_first('.age, .time')
        
        if title_link and title_node:
            url = title_link.attributes.get('href', '')
            if url and "brave.com" not in url and url.startswith('http'):
                
                source_txt = source_node.text().strip() if source_node else "Noticia"
                time_txt = time_node.text().strip() if time_node else ""
                
                content_prefix = f"{source_txt} ({time_txt}): " if time_txt else f"{source_txt}: "
                snippet_txt = snippet_node.text().strip() if snippet_node else ""
                
                results.append({
                    "title": title_node.text().strip(),
                    "url": url,
                    "content": content_prefix + snippet_txt,
                    "source": "brave_news"
                })
    return results
