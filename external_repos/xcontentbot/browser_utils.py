"""Browser utilities for Playwright automation."""
import os
import asyncio
import random
import shutil
import logging
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Page

from config import STATE_PATH, HEADLESS, X_USERNAME, X_PASSWORD, SELECTORS

logger = logging.getLogger("x-mcp")


@asynccontextmanager
async def managed_browser():
    """Async context manager for browser lifecycle."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        ctx = await browser.new_context(
            storage_state=STATE_PATH if os.path.exists(STATE_PATH) else None,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1",
            }
        )
        if not os.path.exists(STATE_PATH):
            await ctx.clear_cookies()
        page = await ctx.new_page()

        await page.route("**/*", lambda route: (
            route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"]
            else route.continue_()
        ))

        try:
            yield page
        finally:
            try:
                os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
                await ctx.storage_state(path=STATE_PATH)
            except Exception as e:
                logger.warning("Failed to persist storage state: %s", e)
            finally:
                await browser.close()


async def with_browser(fn):
    """Run a function with a browser context."""
    async with managed_browser() as page:
        return await fn(page)


async def ensure_logged_in(page: Page) -> None:
    """Ensure the page is authenticated."""
    await asyncio.sleep(1)
    current_url = page.url

    if not current_url.startswith("https://x.com") and not current_url.startswith("https://twitter.com"):
        if "linkedin" in current_url.lower():
            try:
                await page.goto("https://x.com", timeout=30000)
                await page.wait_for_load_state("load", timeout=30000)
                current_url = page.url
            except Exception as e:
                logger.error("Failed to redirect back to X.com: %s", e)

        if not current_url.startswith("https://x.com"):
            raise RuntimeError(f"Not logged in or redirected to {current_url}")

    if "/i/flow/login" in current_url and "redirect_after_login" in current_url:
        raise RuntimeError(f"Session expired. Run x_login_once(). URL: {current_url}")


async def clear_browser_state():
    """Clear all browser state."""
    if os.path.exists(STATE_PATH):
        os.remove(STATE_PATH)
        logger.info("Cleared browser state file: %s", STATE_PATH)

    for cache_dir in ["browser/cache", "browser/storage"]:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)


async def x_login_once():
    """Run once to store logged-in X session."""
    await clear_browser_state()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        await ctx.clear_cookies()
        page = await ctx.new_page()

        await page.goto("https://x.com/login")
        logger.info("Attempting automated login to X...")

        await page.fill(SELECTORS["login_username"], X_USERNAME)
        await page.click(SELECTORS["login_next_button"])
        await asyncio.sleep(random.uniform(1, 2))

        await page.fill(SELECTORS["login_password"], X_PASSWORD)
        await page.click(SELECTORS["login_submit_button"])
        await asyncio.sleep(random.uniform(2, 3))

        print("\n>>> If CAPTCHA or 2FA appears, complete it in the browser.")
        print(">>> Waiting 30 seconds...\n")

        try:
            import signal
            signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError()))
            signal.alarm(30)
            input("Press Enter when ready: ")
            signal.alarm(0)
        except (TimeoutError, EOFError):
            signal.alarm(0)

        if "home" not in page.url:
            raise RuntimeError(f"Login failed; ended at {page.url}")

        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        await ctx.storage_state(path=STATE_PATH)
        await browser.close()
        print(f"Saved session to {STATE_PATH}")


async def dismiss_overlays(page: Page) -> None:
    """Dismiss cookie banners and overlays."""
    candidates = [
        ("Accept", "button:has-text('Accept')"),
        ("Accept all", "button:has-text('Accept all')"),
        ("Close", "button:has-text('Close')"),
        ("Dismiss", "button[aria-label='Dismiss']"),
    ]
    for name, sel in candidates:
        try:
            btn = page.locator(sel).first
            if await btn.count() and await btn.is_visible():
                await btn.click(timeout=2000)
                await asyncio.sleep(0.3)
        except Exception:
            pass


async def apply_posts_filter(page: Page) -> None:
    """Apply 'Top' filter to posts."""
    for sel in ["a[href*='&f=top']", "a:has-text('Top')", "div[role='tab']:has-text('Top')"]:
        try:
            el = page.locator(sel).first
            if await el.count():
                await el.click(timeout=2500)
                await asyncio.sleep(random.uniform(0.5, 1.0))
                return
        except Exception:
            continue
