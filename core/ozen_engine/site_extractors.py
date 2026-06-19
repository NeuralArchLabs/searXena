"""
Site-specific extractors for O-ZEN Engine.

Handles sites that require special extraction strategies:
- Reddit: old.reddit.com HTML + JS challenge resolution
- YouTube: oEmbed API for video metadata

These extractors are part of O-ZEN Engine, not external to it.
"""
import re
import json
import logging
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse, urlencode, parse_qs

from lxml import html as lxml_html
from lxml.etree import Element, SubElement

from .utils import load_html, trim

LOGGER = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Reddit JS Challenge Resolver
# ─────────────────────────────────────────────────────────────────────────────

def detect_reddit_challenge(html_text: str) -> bool:
    """Detect if the page is a Reddit JS verification challenge."""
    if not html_text:
        return False
    return (
        "Please wait for verification" in html_text
        or ("js_challenge" in html_text and "requestSubmit" in html_text)
    )


def solve_reddit_challenge(html_text: str) -> Optional[Dict[str, str]]:
    """
    Extract and solve the Reddit JS challenge.
    
    The challenge is: await(async e => e+e)("hex_string")
    Solution: concatenate the hex string with itself.
    """
    if not html_text:
        return None

    # Extract hex string from the challenge script
    match = re.search(r'\(async\s+e\s*=>\s*e\+e\)\("([a-f0-9]+)"\)', html_text)
    if not match:
        match = re.search(r'e\+e\)\("([a-f0-9]+)"\)', html_text)
    if not match:
        return None

    hex_value = match.group(1)
    solution = hex_value + hex_value

    # Extract token from form
    token_match = re.search(r'name="token"\s+value="([^"]+)"', html_text)
    token = token_match.group(1) if token_match else ""

    jsc_match = re.search(r'name="jsc_orig_r"\s+value="([^"]*)"', html_text)
    jsc_orig_r = jsc_match.group(1) if jsc_match else ""

    LOGGER.debug("Reddit challenge solved: solution=%s...", solution[:20])

    return {
        "solution": solution,
        "js_challenge": "1",
        "token": token,
        "jsc_orig_r": jsc_orig_r,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Reddit Post Extractor
# ─────────────────────────────────────────────────────────────────────────────

def extract_reddit_post(html_text: str, url: str) -> Optional[Dict[str, Any]]:
    """
    Extract a Reddit post and comments from old.reddit.com HTML.
    
    Uses selectolax to parse the traditional HTML structure:
    - div.thing: post container
    - div.usertext-body div.md: post selftext
    - div.comment: comment containers
    
    Returns:
        Dict with {title, author, subreddit, score, selftext, comments} or None
    """
    if not html_text or len(html_text) < 5000:
        return None

    try:
        from selectolax.parser import HTMLParser
    except ImportError:
        return None

    tree = HTMLParser(html_text)
    things = tree.css('div.thing')
    if not things:
        return None

    post = things[0]

    # Extract title
    title_node = post.css_first('a.title, p.title a')
    title = title_node.text().strip() if title_node else "Post de Reddit"

    # Extract selftext (post body)
    selftext_node = post.css_first('div.usertext-body div.md')
    selftext = selftext_node.text().strip() if selftext_node else ""

    # Extract metadata
    author_node = post.css_first('p.tagline a.author, a.author')
    author = author_node.text().strip() if author_node else "unknown"

    score_node = post.css_first('div.score.unvoted')
    score = score_node.text().strip() if score_node else "?"

    subreddit = post.attributes.get('data-subreddit', '')
    if not subreddit:
        m = re.search(r'/r/(\w+)/', url)
        subreddit = m.group(1) if m else 'reddit'

    # Extract comments
    comments = []
    for c in tree.css('div.comment'):
        c_author = c.css_first('a.author')
        c_body = c.css_first('div.usertext-body div.md')
        c_author_text = c_author.text().strip() if c_author else "?"
        c_body_text = c_body.text().strip() if c_body else ""
        if c_body_text and c_body_text not in ("[deleted]", "[removed]"):
            comments.append({
                "author": c_author_text,
                "body": c_body_text
            })

    # Calculate word count
    all_text = selftext + " " + " ".join(c["body"] for c in comments)
    word_count = len(all_text.split())

    if word_count < 5:
        return None

    return {
        "title": title,
        "author": author,
        "subreddit": subreddit,
        "score": score,
        "selftext": selftext,
        "comments": comments[:15],  # Top 15
        "word_count": word_count,
    }


def reddit_markdown_to_html(text: str) -> str:
    """Convert basic Reddit markdown to HTML for Reader Mode."""
    if not text:
        return ""

    # Escape HTML
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Code blocks ```
    text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    return text


def build_reddit_reader_html(post_data: Dict[str, Any], url: str) -> str:
    """Build HTML for Reader Mode from extracted Reddit post data."""
    content_html = f"<article class='reddit-post'>"
    content_html += (
        f"<div class='reddit-meta'>"
        f"<p><strong>r/{post_data['subreddit']}</strong> · "
        f"Posted by u/{post_data['author']} · {post_data['score']} points</p>"
        f"</div>"
    )

    if post_data.get("selftext"):
        for p in post_data["selftext"].split("\n"):
            p = p.strip()
            if p:
                content_html += f"<p>{p}</p>"
    else:
        content_html += f"<p><em>Post de enlace</em></p>"

    if post_data.get("comments"):
        content_html += "<hr/><h3>Comentarios</h3>"
        for c in post_data["comments"]:
            body = c["body"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            content_html += (
                f"<div class='reddit-comment'>"
                f"<p><strong>u/{c['author']}</strong></p>"
                f"<div>{body}</div>"
                f"</div>"
            )

    content_html += "</article>"
    return content_html


# ─────────────────────────────────────────────────────────────────────────────
# YouTube oEmbed Extractor
# ─────────────────────────────────────────────────────────────────────────────

def extract_youtube_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    if "watch" in url:
        match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
    elif "youtu.be" in url:
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
    return None


def build_youtube_oembed_url(video_id: str) -> str:
    """Build the oEmbed API URL for a YouTube video."""
    return f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"


def build_youtube_reader_html(data: Dict[str, str], url: str) -> str:
    """Build HTML for Reader Mode from YouTube oEmbed data."""
    content_html = f"<article class='youtube-video'>"
    if data.get("html"):
        content_html += f"<div class='video-embed'>{data['html']}</div>"
    content_html += f"<h1>{data.get('title', '')}</h1>"
    content_html += f"<p>Canal: <strong>{data.get('author_name', '')}</strong></p>"
    content_html += f"<p><a href='{url}'>Ver en YouTube</a></p>"
    content_html += f"</article>"
    return content_html