"""URL validation and extraction utilities."""
import re
from urllib.parse import urlparse


def extract_status_id(url: str) -> str:
    """Extract status ID from X URL."""
    match = re.search(r'/status/(\d+)', url)
    return match.group(1) if match else ""


def validate_x_url(url: str) -> bool:
    """Validate that URL is from X/Twitter only."""
    if not url:
        return False

    parsed = urlparse(url)
    valid_domains = ['x.com', 'twitter.com']

    domain = parsed.netloc.lower()
    if not any(valid_domain in domain for valid_domain in valid_domains):
        return False

    if '/status/' not in parsed.path:
        return False

    if 'linkedin' in url.lower() or 'urn:li:' in url.lower():
        return False

    return True
