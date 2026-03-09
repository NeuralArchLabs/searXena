from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["videos"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://www.twitch.tv/search?term={query}"

def response(resp):
    results = []
    # Twitch es casi 100% JS, pero podemos intentar capturar data de scripts 
    # o simplemente devolver un link al canal si el match es bueno
    return results # Placeholder for now, Twitch is hard without API
