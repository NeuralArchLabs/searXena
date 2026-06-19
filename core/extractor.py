"""
OZEN Extractor — Wrapper de extracción para searXena.

Delega toda la lógica de extracción al O-ZEN Engine (core/ozen_engine/).
Las mejoras de extracción viven dentro de O-ZEN, no aquí.

Pipeline:
1. APIs públicas nativas (Reddit old.reddit.com, YouTube oEmbed) → O-ZEN site_extractors
2. Extracción O-ZEN estática (baseline mejorado + core)
3. Mensaje informativo si todo falla
"""
import os
import sys
import json
import logging
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse

# --- O-ZEN ENGINE ---
try:
    from .ozen_engine import (
        bare_extraction, extract as ozen_extract, baseline as ozen_baseline,
        detect_reddit_challenge, solve_reddit_challenge,
        extract_reddit_post, build_reddit_reader_html,
        extract_youtube_video_id, build_youtube_oembed_url, build_youtube_reader_html,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ozen_engine import (
        bare_extraction, extract as ozen_extract, baseline as ozen_baseline,
        detect_reddit_challenge, solve_reddit_challenge,
        extract_reddit_post, build_reddit_reader_html,
        extract_youtube_video_id, build_youtube_oembed_url, build_youtube_reader_html,
    )

import httpx
from utils import gen_useragent, detect_block

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("O-ZEN")


class OZENExtractor:
    """Wrapper delgado de extracción. Toda la lógica vive en O-ZEN Engine."""

    def __init__(self, timeout: float = 20.0, cache_ttl: int = 600):
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache = {}
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": gen_useragent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            },
            follow_redirects=True, timeout=timeout, http2=True, verify=False
        )

    async def fetch(self, url: str) -> Optional[tuple]:
        try:
            self.client.headers["User-Agent"] = gen_useragent()
            resp = await self.client.get(url)
            return (resp.text, resp.status_code)
        except Exception as e:
            logger.error(f"O-ZEN Fetch Error: {e}")
            return None

    async def extract(self, url: str) -> Dict[str, Any]:
        now = time.time()

        # 1. Cache
        if url in self._cache:
            data, expiry = self._cache[url]
            if now < expiry:
                return data
            del self._cache[url]

        # 2. Site-specific extraction (Reddit, YouTube) — vive en O-ZEN
        site_result = await self._extract_site_specific(url)
        if site_result and site_result.get("word_count", 0) > 0:
            self._cache[url] = (site_result, now + self.cache_ttl)
            self._prune_cache()
            return site_result

        # 3. Fetch HTTP estático
        fetch_result = await self.fetch(url)
        if not fetch_result:
            return {"error": "Fallo de conexión. No se pudo acceder al sitio de destino."}

        html, status_code = fetch_result
        domain = urlparse(url).netloc

        # 4. HTTP errors
        if status_code in [403, 429, 503]:
            msgs = {
                403: f"Acceso denegado (403). El sitio {domain} ha rechazado la petición.",
                429: f"Demasiadas solicitudes (429). Intenta de nuevo más tarde.",
                503: f"Servicio no disponible (503). El sitio {domain} no está disponible.",
            }
            return {
                "metadata": {"title": f"Error {status_code} — {domain}", "site_name": domain, "url": url},
                "content": f"<div class='error-notice'><h3>⚠️ Error HTTP {status_code}</h3><p>{msgs.get(status_code, '')}</p><p><a href='{url}' target='_blank'>{url}</a></p></div>",
                "word_count": 0, "status": f"http_{status_code}"
            }

        # 5. WAF/Cloudflare detection
        is_blocked, block_reason = detect_block(html, status_code, "")
        if is_blocked:
            return {
                "metadata": {"title": f"Acceso bloqueado — {domain}", "site_name": domain, "url": url},
                "content": f"<div class='block-notice'><h3>⚠️ Contenido no disponible</h3><p>El sitio {domain} está bloqueando el acceso ({block_reason}).</p><p><a href='{url}' target='_blank'>{url}</a></p></div>",
                "word_count": 0, "status": f"blocked_{block_reason}", "block_reason": block_reason
            }

        # 6. O-ZEN extraction (baseline mejorado con estrategias nativas)
        try:
            doc = bare_extraction(
                html, url=url, include_comments=False, include_tables=True,
                include_images=True, include_formatting=True,
                output_format="python", with_metadata=True
            )

            if not doc or not doc.text:
                _, text, _ = ozen_baseline(html)
                if text and len(text) > 100:
                    result = {
                        "metadata": {"title": url, "site_name": urlparse(url).netloc},
                        "content": f"<p>{text}</p>",
                        "word_count": len(text.split()),
                        "status": "success (baseline)"
                    }
                    self._cache[url] = (result, now + self.cache_ttl)
                    self._prune_cache()
                    return result
                return {"error": "No se pudo extraer contenido valioso de la página."}

            content_html = ozen_extract(
                html, url=url, output_format="html",
                include_comments=False, include_images=True, include_tables=True
            )

            result = {
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
            self._cache[url] = (result, now + self.cache_ttl)
            self._prune_cache()
            return result
        except Exception as e:
            logger.error(f"Error en O-ZEN Engine: {e}")
            return {"error": f"Error en el motor O-ZEN: {str(e)}"}

    async def _extract_site_specific(self, url: str) -> Optional[Dict]:
        """Site-specific extraction using O-ZEN's site_extractors module."""
        if not url:
            return None
        domain = urlparse(url).netloc.lower()

        if "reddit.com" in domain and "/comments/" in url:
            return await self._extract_reddit(url)

        if ("youtube.com" in domain or "youtu.be" in domain) and ("watch" in url or "youtu.be" in domain):
            return await self._extract_youtube(url)

        return None

    async def _extract_reddit(self, url: str) -> Optional[Dict]:
        try:
            old_url = url.replace("www.reddit.com", "old.reddit.com")
            if "?" in old_url:
                old_url = old_url.split("?")[0]

            async with httpx.AsyncClient(follow_redirects=True, timeout=20, verify=False, http2=False) as api_client:
                resp = await api_client.get(old_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-US,en;q=0.9",
                })
                cookies = dict(resp.cookies)
                html = resp.text

                if detect_reddit_challenge(html):
                    logger.info("O-ZEN: Reddit challenge detectado, resolviendo...")
                    sol = solve_reddit_challenge(html)
                    if sol:
                        from urllib.parse import urlencode, urlparse as up
                        parsed = up(old_url)
                        challenge_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode({'solution': sol['solution'], 'js_challenge': '1', 'token': sol['token']})}"
                        resp2 = await api_client.get(challenge_url, headers={"User-Agent": "Mozilla/5.0"}, cookies=cookies)
                        cookies.update(dict(resp2.cookies))
                        html = resp2.text

                if len(html) < 5000:
                    return None

                post_data = extract_reddit_post(html, old_url)
                if not post_data:
                    return None

                content_html = build_reddit_reader_html(post_data, url)
                logger.info(f"O-ZEN: Reddit post extraído: {post_data['word_count']} palabras")

                return {
                    "metadata": {
                        "title": post_data["title"], "author": f"u/{post_data['author']}",
                        "date": "", "description": f"Post en r/{post_data['subreddit']}",
                        "image": "", "site_name": f"r/{post_data['subreddit']}", "url": url
                    },
                    "content": content_html,
                    "word_count": post_data["word_count"],
                    "status": "success (reddit old)",
                    "render_method": "reddit_old_html"
                }
        except Exception as e:
            logger.warning(f"Reddit extraction error: {type(e).__name__}: {e}")
            return None

    async def _extract_youtube(self, url: str) -> Optional[Dict]:
        try:
            video_id = extract_youtube_video_id(url)
            if not video_id:
                return None

            oembed_url = build_youtube_oembed_url(video_id)

            async with httpx.AsyncClient(follow_redirects=True, timeout=10, verify=False, http2=False) as api_client:
                resp = await api_client.get(oembed_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                })
                if resp.status_code != 200:
                    return None

                data = resp.json()
                title = data.get("title", "")
                author = data.get("author_name", "")
                thumbnail = data.get("thumbnail_url", "")
                html_embed = data.get("html", "")

                if not title:
                    return None

                content_html = build_youtube_reader_html({"title": title, "author_name": author, "html": html_embed}, url)
                word_count = len((title + " " + author).split())
                logger.info(f"O-ZEN: YouTube oEmbed extrajo '{title[:40]}'")

                return {
                    "metadata": {"title": title, "author": author, "date": "",
                                  "description": f"Video de YouTube por {author}",
                                  "image": thumbnail, "site_name": "YouTube", "url": url},
                    "content": content_html,
                    "word_count": word_count,
                    "status": "success (youtube oembed)",
                    "render_method": "youtube_api"
                }
        except Exception as e:
            logger.warning(f"YouTube oEmbed error: {type(e).__name__}: {e}")
            return None

    def _prune_cache(self):
        if len(self._cache) < 200:
            return
        now = time.time()
        self._cache = {k: v for k, v in self._cache.items() if now < v[1]}
        if len(self._cache) > 300:
            keys = list(self._cache.keys())
            for k in keys[:100]:
                del self._cache[k]

    async def close(self):
        await self.client.aclose()