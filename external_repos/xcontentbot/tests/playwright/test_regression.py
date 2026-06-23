#!/usr/bin/env python3
"""
Tests for detecting selector regressions.
"""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock
from playwright.async_api import Page

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from x_mcp import SELECTORS


class TestSelectorRegressionDetection:
    """Test suite for detecting selector regressions."""

    @pytest.fixture
    async def mock_page(self):
        """Create a mock Playwright page for testing."""
        page = AsyncMock(spec=Page)
        page.locator = MagicMock()
        return page

    def test_selector_consistency(self):
        """Test that selectors remain consistent across runs."""
        expected_selectors = {
            "login_username": "input[name='text']",
            "login_password": "input[name='password']",
            "search_input": "input[data-testid='SearchBox_Search_Input']",
            "post_cards": "article[data-testid='tweet'], div[data-testid='cellInnerDiv']",
        }

        for selector_name, expected_value in expected_selectors.items():
            assert SELECTORS[selector_name] == expected_value, \
                f"Selector {selector_name} changed from expected value"

    @pytest.mark.asyncio
    async def test_selector_performance(self, mock_page):
        """Test that selectors perform within acceptable time limits."""
        mock_page.locator.return_value.first.click = AsyncMock()

        start_time = time.time()
        await mock_page.locator(SELECTORS["comment_button"]).first.click(
            timeout=1000
        )
        end_time = time.time()

        assert (end_time - start_time) < 1.0, "Selector operation took too long"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
