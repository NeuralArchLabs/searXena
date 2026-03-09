from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://gitlab.com/search?search={query}&group_id=&project_id=&scope=projects"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.project-row'):
        title_node = node.css_first('span.project-full-name')
        link_node = node.css_first('a')
        
        if title_node and link_node:
            results.append({
                "title": f"GitLab: {title_node.text().strip()}",
                "url": "https://gitlab.com" + link_node.attributes.get('href', ''),
                "content": "Repositorio en GitLab.",
                "source": "gitlab"
            })
    return results
