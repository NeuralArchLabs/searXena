from selectolax.parser import HTMLParser
from urllib.parse import urlencode

NAME = "osm"
CATEGORIES = ["general", "maps"]
WEIGHT = 3.0 # Alta prioridad en su categoría

def request(query, params):
    # Usar Nominatim API de OpenStreetMap
    params["url"] = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=1"
    params["headers"]["User-Agent"] = "searXena-Agent/1.0"

def response(resp):
    results = []
    try:
        data = resp.json()
        if data:
            place = data[0]
            results.append({
                "title": place.get("display_name"),
                "url": f"https://www.openstreetmap.org/#map=15/{place.get('lat')}/{place.get('lon')}",
                "content": f"Coordenadas: {place.get('lat')}, {place.get('lon')} | Clase: {place.get('class')} | Tipo: {place.get('type')}",
                "template": "infobox.html",
                "source": "osm"
            })
    except:
        pass
    return results
