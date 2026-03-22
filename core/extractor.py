import os
import sys
import json
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

# --- O-ZEN ENGINE INTEGRATION ---
# Integramos el núcleo oficial (anteriormente Trafilatura) como O-ZEN Engine
# Ahora es una parte nativa del código de searXena.
try:
    from .ozen_engine import bare_extraction, extract as ozen_extract, baseline as ozen_baseline
except ImportError:
    # Fallback para ejecución directa o entornos no empaquetados
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ozen_engine import bare_extraction, extract as ozen_extract, baseline as ozen_baseline

import httpx
from utils import gen_useragent

# Configuración de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("O-ZEN")

class ZenaExtractor:
    """
    ZenaExtractor v8 (Powered by O-ZEN Engine):
    El motor de extracción definitivo de searXena.
    Utiliza el núcleo O-ZEN para una precisión quirúrgica en el contenido.
    """
    
    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": gen_useragent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            },
            follow_redirects=True,
            timeout=timeout,
            http2=True,
            verify=False
        )

    async def fetch(self, url: str) -> Optional[str]:
        try:
            self.client.headers["User-Agent"] = gen_useragent()
            resp = await self.client.get(url)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            logger.error(f"O-ZEN Fetch Error: {e}")
        return None

    async def extract(self, url: str) -> Dict[str, Any]:
        """
        Extrae el contenido de una URL utilizando el motor O-ZEN.
        """
        html = await self.fetch(url)
        if not html:
            return {"error": "Fallo de conexión o bloqueo en el sitio de destino."}
        
        try:
            # Obtener metadatos con bare_extraction
            doc = bare_extraction(
                html, 
                url=url, 
                include_comments=False, 
                include_tables=True, 
                include_images=True,
                include_formatting=True,
                output_format="python",
                with_metadata=True
            )
            
            if not doc or not doc.text:
                logger.info(f"O-ZEN: Extracción estructural falló en {url}, iniciando rescate baseline.")
                _, text, _ = ozen_baseline(html)
                if text and len(text) > 100:
                    return {
                        "metadata": {"title": url, "site_name": urlparse(url).netloc},
                        "content": f"<p>{text}</p>",
                        "word_count": len(text.split()),
                        "status": "success (baseline)"
                    }
                return {"error": "No se pudo extraer contenido valioso de la página."}

            # Obtener el HTML limpio para el Reader Mode
            content_html = ozen_extract(
                html, 
                url=url, 
                output_format="html",
                include_comments=False,
                include_images=True,
                include_tables=True
            )

            return {
                "metadata": {
                    "title": doc.title or "Sin título",
                    "author": doc.author or "",
                    "date": doc.date or "",
                    "description": doc.description or "",
                    "image": doc.image or "",
                    "site_name": doc.sitename or urlparse(url).netloc,
                    "url": doc.url or url
                },
                "content": content_html,
                "word_count": len((doc.text or "").split()),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error crítico en O-ZEN Engine: {e}")
            return {"error": f"Error en el motor O-ZEN: {str(e)}"}

    async def close(self):
        await self.client.aclose()
