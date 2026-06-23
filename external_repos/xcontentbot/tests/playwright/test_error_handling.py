#!/usr/bin/env python3
"""
Tests for error handling and resilience in Playwright operations.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
import httpx

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from x_client import fetch_posts


class TestErrorHandling:
    """Test suite for error handling and resilience."""

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(httpx.TimeoutException):
                await fetch_posts(mock_client, "burnout", 10)

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of connection errors."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")

            with pytest.raises(httpx.ConnectError):
                await fetch_posts(mock_client, "burnout", 10)

    @pytest.mark.asyncio
    async def test_invalid_json_response(self):
        """Test handling of invalid JSON responses."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError(
                "Invalid JSON", "", 0
            )
            mock_client.get.return_value = mock_response

            with pytest.raises(json.JSONDecodeError):
                await fetch_posts(mock_client, "burnout", 10)
