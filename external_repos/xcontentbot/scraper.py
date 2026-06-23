"""X post scraping functionality."""
import asyncio
import random
import re
import logging
from typing import List, Dict
from urllib.parse import quote_plus
from playwright.async_api import Page

from browser_utils import ensure_logged_in, dismiss_overlays, apply_posts_filter
from url_utils import extract_status_id, validate_x_url

logger = logging.getLogger("x-mcp")

# In-memory post storage
POSTS: Dict[str, Dict] = {}


async def harvest_by_href(page: Page, limit: int) -> List[Dict]:
    """Harvest posts by scanning all status links."""
    raw = await page.evaluate("""() => {
        const anchors = Array.from(document.querySelectorAll("a[href*='/status/']"));
        const seen = new Set();
        const out = [];
        for (const a of anchors) {
            let href = a.href;
            if (!href) continue;
            if (href.includes('linkedin.com')) continue;
            if (href.startsWith('/')) href = 'https://x.com' + href;
            if (!href.includes('x.com') && !href.includes('twitter.com')) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            const art = a.closest("article");
            const text = (art?.innerText || "").slice(0, 8000);
            out.push({ href, text });
        }
        return out;
    }""")

    items = []
    seen_ids = set()
    for row in raw[:limit]:
        url = row.get("href")
        text = row.get("text") or ""
        if not url or not validate_x_url(url):
            continue
        post_id = extract_status_id(url)
        if not post_id or post_id in seen_ids:
            continue
        seen_ids.add(post_id)
        full_url = f"https://x.com/i/status/{post_id}"
        item = {"id": post_id, "url": full_url, "author": None, "text_preview": text[:220]}
        POSTS[post_id] = {"id": post_id, "url": full_url, "author": None, "text": text}
        items.append(item)
    return items


async def search_x_internal(page: Page, query: str, limit: int) -> List[Dict]:
    """Internal search implementation."""
    limit = max(1, min(int(limit), 25))
    q = quote_plus(query)

    search_urls = [
        f"https://x.com/search?q={q}&src=typed_query&f=top",
        f"https://x.com/search?q={q}&src=typed_query",
    ]

    results: List[Dict] = []
    seen_ids = set()
    result_selector = "article[data-testid='tweet'], div[data-testid='cellInnerDiv']"

    for idx, url in enumerate(search_urls):
        logger.info("Opening X search (%d/%d): %s", idx + 1, len(search_urls), url)
        await page.goto(url)
        await page.wait_for_load_state("load", timeout=60000)
        await ensure_logged_in(page)

        if 'linkedin.com' in page.url.lower():
            raise RuntimeError(f"Unexpected redirect to LinkedIn: {page.url}")

        await dismiss_overlays(page)
        await asyncio.sleep(random.uniform(0.6, 1.2))
        await apply_posts_filter(page)
        await asyncio.sleep(random.uniform(0.4, 0.9))

        try:
            await page.wait_for_function(
                """() => !!document.querySelector("a[href*='/status/']")""",
                timeout=15000,
            )
        except Exception:
            pass

        had_containers = False
        try:
            await page.wait_for_selector(result_selector, timeout=12000)
            had_containers = True
        except Exception:
            pass

        if had_containers:
            cards = await page.locator(result_selector).all()
            for card in cards:
                try:
                    link = card.locator("a[href*='/status/'] time[datetime]").first
                    if not await link.count():
                        continue
                    href = await link.evaluate("el => el.closest('a').href")
                    if not href or not validate_x_url(href):
                        continue
                    post_id = extract_status_id(href)
                    if not post_id or post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)
                    user_match = re.search(r'https://x\.com/([^/]+)/status/', href)
                    user = user_match.group(1) if user_match else None
                    full_url = f"https://x.com/{user}/status/{post_id}" if user else f"https://x.com/i/status/{post_id}"
                    text = (await card.inner_text())[:8000]
                    item = {"id": post_id, "url": full_url, "author": None, "text_preview": text[:220]}
                    POSTS[post_id] = {"id": post_id, "url": full_url, "author": None, "text": text}
                    results.append(item)
                    if len(results) >= limit:
                        break
                except Exception:
                    pass

        if len(results) < limit:
            extra = await harvest_by_href(page, limit - len(results))
            for it in extra:
                if it["id"] not in seen_ids:
                    seen_ids.add(it["id"])
                    results.append(it)
                    if len(results) >= limit:
                        break

        if results:
            break

    logger.info("Found %d posts", len(results))
    return results[:limit]


def validate_x_results(results: List[Dict]) -> List[Dict]:
    """Validate that all results are X posts."""
    valid = []
    for result in results:
        url = result.get('url', '')
        if 'linkedin.com' in url.lower():
            continue
        if 'x.com' in url.lower() or 'twitter.com' in url.lower():
            valid.append(result)
    return valid
