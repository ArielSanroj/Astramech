#!/usr/bin/env python3
"""
Tests for xMCP API flow and error handling.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
import httpx

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from x_client import fetch_posts, get_post, draft_comment, submit_comment


class TestXMCPFlow:
    """Test suite for xMCP API flow and error handling."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock httpx client for testing."""
        client = AsyncMock(spec=httpx.AsyncClient)
        return client

    @pytest.fixture
    def sample_search_response(self):
        """Sample search response data."""
        return [
            {
                "id": "test_post_1",
                "url": "https://x.com/user1/status/123",
                "author": "user1",
                "text_preview": "Sample post about burnout..."
            },
            {
                "id": "test_post_2",
                "url": "https://x.com/user2/status/456",
                "author": "user2",
                "text_preview": "Another post about productivity..."
            }
        ]

    @pytest.mark.asyncio
    async def test_search_posts_success(
        self, mock_httpx_client, sample_search_response
    ):
        """Test successful search posts API call."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_httpx_client.get.return_value = mock_response

        result = await fetch_posts(mock_httpx_client, "burnout", 10)
        assert result == sample_search_response
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_posts_http_error(self, mock_httpx_client):
        """Test search posts with HTTP error handling."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=AsyncMock(), response=mock_response
        )
        mock_httpx_client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await fetch_posts(mock_httpx_client, "burnout", 10)

    @pytest.mark.asyncio
    async def test_get_post_success(self, mock_httpx_client):
        """Test successful get post API call."""
        sample_post = {
            "id": "test_post_1",
            "url": "https://x.com/user1/status/123",
            "author": "user1",
            "text": "Full post text about burnout and productivity"
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_post
        mock_httpx_client.get.return_value = mock_response

        result = await get_post(mock_httpx_client, "test_post_1")
        assert result == sample_post

    @pytest.mark.asyncio
    async def test_draft_comment_success(self, mock_httpx_client):
        """Test successful draft comment API call."""
        sample_draft = {
            "id": "test_post_1",
            "comment": "This is a draft comment about the post"
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_draft
        mock_httpx_client.get.return_value = mock_response

        result = await draft_comment(mock_httpx_client, "test_post_1")
        assert result == sample_draft

    @pytest.mark.asyncio
    async def test_submit_comment_success(self, mock_httpx_client):
        """Test successful submit comment API call."""
        sample_result = {
            "status": "posted",
            "id": "test_post_1",
            "comment": "This is the posted comment"
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_result
        mock_httpx_client.post.return_value = mock_response

        result = await submit_comment(
            mock_httpx_client, "test_post_1", "Test comment", True
        )
        assert result == sample_result

    @pytest.mark.asyncio
    async def test_submit_comment_preview_mode(self, mock_httpx_client):
        """Test submit comment in preview mode."""
        sample_result = {
            "status": "preview",
            "id": "test_post_1",
            "comment": "This is a preview comment"
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_result
        mock_httpx_client.post.return_value = mock_response

        result = await submit_comment(
            mock_httpx_client, "test_post_1", "Test comment", False
        )
        assert result == sample_result
        assert result["status"] == "preview"
