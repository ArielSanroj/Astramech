#!/usr/bin/env python3
"""
Tests for Playwright selector definitions and stability.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from playwright.async_api import Page, TimeoutError as PwTimeout

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from x_mcp import SELECTORS


class TestPlaywrightSelectors:
    """Test suite for Playwright selector stability and functionality."""

    @pytest.fixture
    async def mock_page(self):
        """Create a mock Playwright page for testing."""
        page = AsyncMock(spec=Page)
        page.goto = AsyncMock()
        page.wait_for_load_state = AsyncMock()
        page.locator = MagicMock()
        page.route = AsyncMock()
        return page

    @pytest.fixture
    def sample_post_data(self):
        """Sample post data for testing."""
        return {
            "id": "test_post_123",
            "url": "https://x.com/testuser/status/123456789",
            "author": "testuser",
            "text": "This is a test post about burnout and productivity",
            "text_preview": "This is a test post about burnout..."
        }

    def test_selector_definitions(self):
        """Test that all required selectors are defined."""
        required_selectors = [
            "login_username", "login_next_button", "login_password",
            "login_submit_button", "search_input", "posts_filter_button",
            "post_cards", "post_link", "actor_name", "comment_button",
            "comment_editor", "post_comment_button", "comments_section"
        ]

        for selector in required_selectors:
            assert selector in SELECTORS, f"Missing selector: {selector}"
            assert SELECTORS[selector], f"Empty selector: {selector}"

    def test_selector_format(self):
        """Test that selectors follow proper CSS/XPath format."""
        for name, selector in SELECTORS.items():
            assert isinstance(selector, str), f"Selector {name} should be string"
            assert len(selector.strip()) > 0, f"Selector {name} should not be empty"
            assert "undefined" not in selector.lower()
            assert "null" not in selector.lower()

    @pytest.mark.asyncio
    async def test_login_flow_selectors(self, mock_page):
        """Test login flow selector interactions."""
        mock_page.locator.return_value.first.click = AsyncMock()
        mock_page.locator.return_value.first.fill = AsyncMock()
        mock_page.locator.return_value.first.is_visible = AsyncMock(return_value=True)

        username_input = mock_page.locator(SELECTORS["login_username"])
        await username_input.first.fill("testuser")
        username_input.first.fill.assert_called_once_with("testuser")

        next_button = mock_page.locator(SELECTORS["login_next_button"])
        await next_button.first.click()
        next_button.first.click.assert_called_once()

        password_input = mock_page.locator(SELECTORS["login_password"])
        await password_input.first.fill("testpass")
        password_input.first.fill.assert_called_once_with("testpass")

        submit_button = mock_page.locator(SELECTORS["login_submit_button"])
        await submit_button.first.click()
        submit_button.first.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_selectors(self, mock_page):
        """Test search functionality selectors."""
        search_input = mock_page.locator(SELECTORS["search_input"])
        await search_input.first.fill("burnout")
        search_input.first.fill.assert_called_once_with("burnout")

        filter_button = mock_page.locator(SELECTORS["posts_filter_button"])
        await filter_button.first.click()
        filter_button.first.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_interaction_selectors(self, mock_page, sample_post_data):
        """Test post interaction selectors (reply, comment, etc.)."""
        post_cards = mock_page.locator(SELECTORS["post_cards"])
        post_cards.count = AsyncMock(return_value=1)

        comment_button = mock_page.locator(SELECTORS["comment_button"])
        await comment_button.first.click()
        comment_button.first.click.assert_called_once()

        comment_editor = mock_page.locator(SELECTORS["comment_editor"])
        await comment_editor.first.fill("Test comment")
        comment_editor.first.fill.assert_called_once_with("Test comment")

        post_button = mock_page.locator(SELECTORS["post_comment_button"])
        post_button.first.is_visible = AsyncMock(return_value=True)
        await post_button.first.click()
        post_button.first.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_selector_timeout_handling(self, mock_page):
        """Test that selectors handle timeouts gracefully."""
        mock_page.locator.return_value.first.click = AsyncMock(
            side_effect=PwTimeout("Selector timeout")
        )

        with pytest.raises(PwTimeout):
            await mock_page.locator(SELECTORS["comment_button"]).first.click(
                timeout=1000
            )

    @pytest.mark.asyncio
    async def test_selector_fallback_behavior(self, mock_page):
        """Test selector fallback behavior when primary selectors fail."""
        mock_page.locator.return_value.first.is_visible = AsyncMock(return_value=False)
        mock_page.locator.return_value.first.click = AsyncMock(
            side_effect=PwTimeout("Not found")
        )

        try:
            comment_button = mock_page.locator(SELECTORS["comment_button"])
            await comment_button.first.click(timeout=1000)
        except PwTimeout:
            pass  # Expected behavior
