"""Configuration and constants for X MCP Server."""
import os
from dotenv import load_dotenv

load_dotenv()

# Server config
AUTO_POST = os.getenv("AUTO_POST", "false").lower() == "true"
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_HOUR", "6"))
BRAND_VOICE = os.getenv("BRAND_VOICE", "clio").lower()
USE_MCP_MODE = os.getenv("USE_MCP_MODE", "false").lower() == "true"
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Browser paths
STATE_PATH = "browser/storage/state.json"

# Credentials
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")

if not X_USERNAME or not X_PASSWORD:
    import logging as _log
    _log.getLogger("config").warning("X_USERNAME and X_PASSWORD not set — bot features disabled, health endpoint available")

# X selectors (keep in one place for quick edits)
SELECTORS = {
    "login_username": "input[name='text']",
    "login_next_button": "button[data-testid='ocf_SignupNextButton'], button:has-text('Next')",
    "login_password": "input[name='password']",
    "login_submit_button": "button[data-testid='ocf_LoginButton'], button:has-text('Log in')",
    "search_input": "input[data-testid='SearchBox_Search_Input']",
    "posts_filter_button": "a[href*='&f=top'], a:has-text('Top')",
    "post_cards": "article[data-testid='tweet'], div[data-testid='cellInnerDiv']",
    "post_link": "a[href*='/status/'] time[datetime]",
    "actor_name": "div[data-testid='User-Name'], span:has-text('@')",
    "comment_button": "div[data-testid='reply']",
    "comment_editor": "div[data-testid*='tweetTextarea']",
    "post_comment_button": "button[data-testid='tweetButtonInline'], button:has-text('Post')",
    "comments_section": "div[data-testid='conversation'], article[data-testid='tweet']",
}
