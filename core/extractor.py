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
import re
import time
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, urljoin, quote_plus

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

            # --- Post-process: clean ad placeholder labels ---
            content_html = self._clean_ad_placeholders(content_html)

            # --- Post-process: recover any images missed by O-ZEN ---
            content_html = self._inject_missing_images(content_html, html, url)

            # Hero image from metadata
            hero_image = (doc.image or "").strip()
            # If og:image is in content already, no need to show it twice
            if hero_image and quote_plus(hero_image) in (content_html or ""):
                hero_image = ""

            result = {
                "metadata": {
                    "title": doc.title or "Sin título",
                    "author": doc.author or "",
                    "date": doc.date or "",
                    "description": doc.description or "",
                    "image": doc.image or "",
                    "hero_image": hero_image,
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
            return {"error": f"Error en O-ZEN Engine: {e}"}

    def _inject_missing_images(self, content_html: Optional[str], raw_html: str, page_url: str) -> Optional[str]:
        """
        Scan raw HTML for images that O-ZEN missed (lazy-loading, srcset-only patterns).
        Uses a two-phase approach:
          1. Prune known boilerplate sections (related posts, sidebars, ads, nav) first.
          2. Only accept images that are genuine article content, not external link thumbnails.
        Hard cap: 8 images maximum to avoid flooding the reader.
        """
        if not content_html or not raw_html:
            return content_html

        try:
            from copy import deepcopy
            from urllib.parse import unquote_plus, urlparse as _urlparse, urljoin
            from lxml.html import fromstring as html_fromstring
            from lxml.etree import strip_elements

            tree = html_fromstring(raw_html)
            page_domain = _urlparse(page_url).netloc.lower().lstrip('www.')

            # ── Phase 1: prune boilerplate containers ────────────────────────────
            # Any element whose class/id contains these strings is considered noise
            BOILERPLATE_KEYWORDS = (
                'related', 'recommend', 'suggestion', 'you-may', 'you-might',
                'more-from', 'also-read', 'more-on', 'trending', 'popular',
                'sidebar', 'widget', 'aside', 'newsletter', 'subscribe',
                'advertisement', 'adsense', 'promo', 'sponsor', 'promoted',
                'comment', 'disqus', 'navigation', 'breadcrumb', 'pagination',
                'footer', 'header', 'menu', 'nav-', '-nav', 'social-share',
                'share-', '-share', 'tag-cloud', 'author', 'avatar', 'profile', 'bio',
                'cookie', 'gdpr', 'banner', 'sticky', 'modal', 'popup',
                'outbrain', 'taboola', 'revcontent', 'zergnet',
            )

            work_tree = deepcopy(tree)
            to_remove = []
            for el in work_tree.iter('*'):
                el_class = (el.get('class') or '').lower()
                el_id    = (el.get('id')    or '').lower()
                combined = el_class + ' ' + el_id
                if any(kw in combined for kw in BOILERPLATE_KEYWORDS):
                    to_remove.append(el)
            # Remove collected elements (parent-first to avoid stale refs)
            removed_ids = set()
            for el in to_remove:
                try:
                    el_id = id(el)
                    if el_id not in removed_ids and el.getparent() is not None:
                        el.getparent().remove(el)
                        removed_ids.add(el_id)
                except Exception:
                    pass

            def _normalize_img_url(url_str: str) -> str:
                """Normalize image URLs by stripping common size patterns and query arguments for deduplication."""
                try:
                    parsed = _urlparse(url_str)
                    path = parsed.path.lower()
                    
                    # Remove common size/resolution patterns: -150x150, _840_560, -500x333, _500_333, etc.
                    path = re.sub(r'[-_]\d+x\d+(?=\.[a-z]{3,4}$)', '', path)
                    path = re.sub(r'[-_]\d+_\d+(?=\.[a-z]{3,4}$)', '', path)
                    
                    # Strip specific folder structures containing resolutions if they occur (e.g. /width/500/)
                    path = re.sub(r'/width/\d+/', '/', path)
                    path = re.sub(r'/height/\d+/', '/', path)
                    
                    # Remove size query params: ?w=500, ?width=500, ?resize=500, etc.
                    query = parsed.query.lower()
                    query = re.sub(r'(width|height|w|h|resize|size|scale|fit)=\d+&?', '', query)
                    query = query.rstrip('&')
                    
                    norm = f"{parsed.netloc}{path}"
                    if query:
                        norm += f"?{query}"
                    return norm
                except Exception:
                    return url_str.lower()

            # ── Phase 2: collect already-proxified images from extracted content ─
            existing_srcs: set = set()
            existing_re = re.compile(r'proxify\?url=([^"&\s]+)')
            for m in existing_re.finditer(content_html):
                existing_srcs.add(unquote_plus(m.group(1)))
            
            existing_normalized = {_normalize_img_url(src) for src in existing_srcs}

            # ── Phase 3: find candidate images in the pruned tree ────────────────
            # Priority order: article > main > generic content containers
            candidate_xpaths = [
                './/article//img',
                './/main//img',
                './/*[contains(@class,"article-body")]//img',
                './/*[contains(@class,"article-content")]//img',
                './/*[contains(@class,"post-content")]//img',
                './/*[contains(@class,"entry-content")]//img',
                './/*[contains(@class,"story-body")]//img',
                './/*[contains(@class,"article")]//img',
                './/*[contains(@class,"content")]//img',
            ]

            def _resolve_img(img_el) -> Optional[str]:
                """Extract the best available image URL from an element."""
                # Direct src attributes, prioritise data-src patterns (lazy loading)
                for attr in ('data-src', 'data-lazy-src', 'data-original',
                             'data-lazy', 'data-image', 'data-full-src', 'src'):
                    val = (img_el.get(attr) or '').strip()
                    if val and val.startswith('http'):
                        return val
                # srcset / data-srcset — pick the widest entry
                for attr in ('srcset', 'data-srcset'):
                    srcset = (img_el.get(attr) or '').strip()
                    if srcset:
                        best_url, best_w = '', 0
                        for entry in srcset.split(','):
                            parts = entry.strip().split()
                            if not parts or not parts[0].startswith('http'):
                                continue
                            w = 0
                            if len(parts) > 1:
                                try:
                                    w = int(parts[1].rstrip('w'))
                                except ValueError:
                                    pass
                            if w > best_w:
                                best_w, best_url = w, parts[0]
                        if best_url:
                            return best_url
                # Relative URL fallback
                src = (img_el.get('src') or '').strip()
                if src and not src.startswith('data:'):
                    return urljoin(page_url, src)
                return None

            def _is_inside_external_link(img_el) -> bool:
                """Return True if the image is wrapped in an <a> pointing to a different page/article."""
                current = img_el.getparent()
                depth = 0
                while current is not None and depth < 5:
                    if current.tag == 'a':
                        href = (current.get('href') or '').strip()
                        if href:
                            abs_href = urljoin(page_url, href)
                            parsed_link = _urlparse(abs_href)
                            link_domain = parsed_link.netloc.lower().lstrip('www.')
                            
                            # If it's a link directly to an image file (lightbox), don't treat it as external article
                            if any(parsed_link.path.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg')):
                                break
                            
                            # If pointing to a different domain, it's an external link
                            if link_domain != page_domain:
                                return True
                                
                            # If pointing to the same domain but a different path, it's a related article link
                            page_path = _urlparse(page_url).path.rstrip('/')
                            link_path = parsed_link.path.rstrip('/')
                            if page_path != link_path:
                                return True
                        break
                    current = current.getparent()
                    depth += 1
                return False

            def _is_inside_boilerplate(img_el) -> bool:
                """Double-check: traverse ancestors for boilerplate markers."""
                current = img_el.getparent()
                depth = 0
                while current is not None and depth < 8:
                    el_class = (current.get('class') or '').lower()
                    el_id    = (current.get('id')    or '').lower()
                    combined = el_class + ' ' + el_id
                    if any(kw in combined for kw in BOILERPLATE_KEYWORDS):
                        return True
                    current = current.getparent()
                    depth += 1
                return False

            # URL and ALT fragments to always skip
            NOISE_TERMS = (
                'pixel', 'tracking', 'beacon', '.svg', 'logo', 'avatar',
                'author', 'profile', 'byline', 'placeholder', 'spinner', 'spacer',
                '1x1', '0x0', 'blank', 'gravatar', 'wp-includes', 'comentario',
                'comment', 'button', 'badge', 'ad-', '-ad', 'advertisement',
                'banner', 'newsletter', 'subscribe'
            )

            seen: set = set()
            seen_normalized: set = set()
            recovered_imgs: list = []
            MAX_IMAGES = 6  # hard cap — keep the reader focused

            for xpath in candidate_xpaths:
                if len(recovered_imgs) >= MAX_IMAGES:
                    break
                for img in work_tree.xpath(xpath):
                    if len(recovered_imgs) >= MAX_IMAGES:
                        break

                    img_url = _resolve_img(img)
                    if not img_url:
                        continue

                    norm_url = _normalize_img_url(img_url)
                    if img_url in seen or norm_url in seen_normalized or norm_url in existing_normalized:
                        continue

                    # Grab alt early to check it for noise
                    alt = (img.get('alt') or '').strip()

                    # Skip noise in URLs and ALTs
                    if any(p in img_url.lower() for p in NOISE_TERMS) or any(p in alt.lower() for p in NOISE_TERMS):
                        continue

                    # Skip tiny declared dimensions (icons / thumbnails)
                    try:
                        w = int(img.get('width', 300))
                        h = int(img.get('height', 200))
                        if w < 150 or h < 80:
                            continue
                    except (ValueError, TypeError):
                        pass

                    # Skip images inside external/related-article links
                    if _is_inside_external_link(img):
                        continue

                    # Belt-and-suspenders boilerplate check on the original tree
                    if _is_inside_boilerplate(img):
                        continue

                    seen.add(img_url)
                    seen_normalized.add(norm_url)

                    # Grab figcaption if the parent is a <figure>
                    parent = img.getparent()
                    caption = ''
                    if parent is not None and parent.tag == 'figure':
                        fig_cap = parent.find('.//figcaption')
                        if fig_cap is not None:
                            caption = (fig_cap.text_content() or '').strip()

                    recovered_imgs.append((img_url, alt, caption or alt))

            if not recovered_imgs:
                return content_html

            # ── Phase 4: build and inject the gallery ─────────────────────────────
            img_blocks = []
            for img_url, alt, caption in recovered_imgs:
                proxified = f"/proxify?url={quote_plus(img_url)}"
                safe_caption = caption.replace('<', '&lt;').replace('>', '&gt;')
                cap_html = (f'<figcaption class="reader-img-caption">{safe_caption}</figcaption>'
                            if safe_caption else '')
                img_blocks.append(
                    f'<figure class="reader-recovered-img">'
                    f'<img src="{proxified}" alt="{alt}" loading="lazy">'
                    f'{cap_html}</figure>'
                )

            gallery_section = (
                f'<div class="recovered-images-section">'
                f'<hr class="reader-divider">'
                + '\n'.join(img_blocks) +
                f'</div>'
            )

            for closing in ('</body>', '</html>'):
                if closing in content_html:
                    return content_html.replace(closing, gallery_section + closing, 1)
            return content_html + gallery_section

        except Exception as e:
            logger.warning(f"Image recovery failed: {e}")
            return content_html

    def _clean_ad_placeholders(self, content_html: Optional[str]) -> Optional[str]:
        """Remove any elements (paragraphs, divs, etc.) that contain only ad labels (e.g. 'PUBLICIDAD')."""
        if not content_html:
            return content_html

        try:
            from lxml.html import fromstring as html_fromstring, tostring
            
            # Check if it has html or body tags
            has_html_wrapper = ('<html' in content_html.lower() or '<body' in content_html.lower())
            
            if not has_html_wrapper:
                tree = html_fromstring(f"<div>{content_html}</div>")
            else:
                tree = html_fromstring(content_html)
            
            AD_LABELS = {
                'publicidad', 'anuncio', 'anuncios', 'advertisement', 'advertising',
                'sponsored', 'patrocinado', 'patrocinados', 'promo', 'promocion',
                'promoción', 'ads', 'ad'
            }
            
            to_remove = []
            for el in tree.iter('*'):
                if el.tag in ('p', 'div', 'span', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                    text = (el.text_content() or '').strip()
                    if text:
                        cleaned = ''.join(c for c in text if c.isalnum() or c.isspace()).lower().strip()
                        if cleaned in AD_LABELS:
                            to_remove.append(el)
            
            # Remove elements (parent-first to avoid stale refs)
            removed_ids = set()
            for el in to_remove:
                try:
                    el_id = id(el)
                    if el_id not in removed_ids and el.getparent() is not None:
                        el.getparent().remove(el)
                        removed_ids.add(el_id)
                except Exception:
                    pass
            
            res = tostring(tree, encoding='utf-8').decode('utf-8')
            if not has_html_wrapper:
                if res.startswith('<div>') and res.endswith('</div>'):
                    res = res[5:-6]
                elif '<body>' in res:
                    start = res.find('<body>') + 6
                    end = res.rfind('</body>')
                    res = res[start:end]
            return res
            
        except Exception as e:
            logger.warning(f"Error cleaning ad placeholders: {e}")
            return content_html

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