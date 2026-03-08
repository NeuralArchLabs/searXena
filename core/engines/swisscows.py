from selectolax.parser import HTMLParser
import urllib.parse

def request(query, params):
    encoded_query = urllib.parse.quote(query)
    params["url"] = f"https://swisscows.com/en/web?query={encoded_query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('article.web-item'):
        title = node.css_first('h2, a.title')
        link = node.css_first('a')
        snippet = node.css_first('p.description, div.snippet')
        
        if title and link:
            href = link.attributes.get('href', '')
            if href.startswith('http'):
                results.append({
                    "title": title.text().strip(),
                    "url": href,
                    "content": snippet.text().strip() if snippet else "Swisscows web result."
                })
    return results
