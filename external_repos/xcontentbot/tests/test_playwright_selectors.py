#!/usr/bin/env python3
"""
Comprehensive test suite for Playwright selectors and xMCP flow.
Tests selector stability, error handling, and regression detection.

This module re-exports from the playwright test package for backwards compatibility.
"""

# Re-export all test classes for backwards compatibility
from tests.playwright.test_selectors import TestPlaywrightSelectors
from tests.playwright.test_xmcp_flow import TestXMCPFlow
from tests.playwright.test_error_handling import TestErrorHandling
from tests.playwright.test_regression import TestSelectorRegressionDetection

import pytest

__all__ = [
    "TestPlaywrightSelectors",
    "TestXMCPFlow",
    "TestErrorHandling",
    "TestSelectorRegressionDetection",
]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
