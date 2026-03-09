import re
import random
from typing import Optional

def extr(text: str, start: str, end: str) -> Optional[str]:
    """Extrae texto entre dos delimitadores (SearXNG style)"""
    try:
        s = text.find(start)
        if s == -1: return None
        s += len(start)
        e = text.find(end, s)
        if e == -1: return None
        return text[s:e]
    except:
        return None

def gen_useragent() -> str:
    """Genera un User-Agent de escritorio moderno aleatorio"""
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
    ]
    return random.choice(agents)

def eval_xpath(tree, path: str):
    """Fallback para selectolax si se portan fragmentos de lxml"""
    # En selectolax usamos css, pero si necesitamos algo específico...
    return tree.css(path)

async def fetch_vqd(query: str, client) -> Optional[str]:
    """Obtiene el token VQD de DuckDuckGo para motores de medios/noticias"""
    try:
        resp = await client.get(f"https://duckduckgo.com/?q={query}", follow_redirects=True)
        vqd = extr(resp.text, 'vqd="', '"') or extr(resp.text, "vqd='", "'")
        return vqd
    except Exception:
        return None
