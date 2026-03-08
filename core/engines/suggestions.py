import httpx
import json
import asyncio

# Usar el backend de Google Autocomplete (usado por SearXNG como predeterminado por su velocidad)
AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search?client=chrome&q="

# Cache simple para sugerencias (evitar peticiones repetitivas en ms)
_suggestion_cache = {}

async def get_suggestions(query: str):
    if not query or len(query) < 2:
        return []
    
    # Check cache
    if query in _suggestion_cache:
        val, ts = _suggestion_cache[query]
        if asyncio.get_event_loop().time() - ts < 3600:
            return val

    try:
        # Petición ultra-veloz con timeout agresivo de 0.5s
        async with httpx.AsyncClient(timeout=0.5) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            resp = await client.get(f"{AUTOCOMPLETE_URL}{query}", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                suggestions = data[1][:6] # Top 6 sugerencias
                _suggestion_cache[query] = (suggestions, asyncio.get_event_loop().time())
                return suggestions
    except Exception:
        pass
    return []
