#!/usr/bin/env python3
"""
Integration tests for system flow with all systems working together.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
class TestSystemIntegration:
    """Test integration between all systems."""

    @pytest.mark.asyncio
    async def test_complete_post_processing_flow(
        self,
        mock_config_manager,
        mock_observability,
        mock_circuit_breaker_manager,
        mock_throttle_manager,
        mock_llm_orchestrator,
        sample_post_data
    ):
        """Test complete post processing flow with all systems."""
        with patch('x_client.fetch_posts') as mock_fetch, \
             patch('x_client.get_post') as mock_get, \
             patch('x_client.draft_comment') as mock_draft, \
             patch('x_client.submit_comment') as mock_submit:

            mock_fetch.return_value = [sample_post_data]
            mock_get.return_value = sample_post_data
            mock_draft.return_value = {
                "id": sample_post_data["id"],
                "comment": "Test comment"
            }
            mock_submit.return_value = {
                "status": "posted",
                "id": sample_post_data["id"]
            }

            post_id = sample_post_data["id"]
            query = "test query"

            metrics = mock_observability.start_post_processing(post_id, query)
            assert metrics.post_id == post_id
            assert metrics.query == query
            assert metrics.status == "pending"

            await asyncio.sleep(0.1)

            mock_observability.record_api_call(post_id, "fetch_posts", True, 0.1)
            mock_observability.record_api_call(post_id, "get_post", True, 0.05)
            mock_observability.record_api_call(post_id, "draft_comment", True, 0.2)
            mock_observability.record_api_call(post_id, "submit_comment", True, 0.3)

            mock_observability.end_post_processing(post_id, "success")

            health_status = mock_observability.get_health_status()
            assert health_status["status"] in ["healthy", "degraded", "unhealthy"]
            assert "metrics" in health_status

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, mock_circuit_breaker_manager):
        """Test circuit breaker integration with API calls."""
        breaker = mock_circuit_breaker_manager.get_breaker("api_calls")

        async def failing_function():
            raise Exception("API Error")

        with pytest.raises(Exception):
            await breaker.call(failing_function)

        metrics = breaker.get_metrics()
        assert metrics["total_calls"] == 1
        assert metrics["total_failures"] == 1
        assert metrics["total_successes"] == 0

    @pytest.mark.asyncio
    async def test_throttling_integration(self, mock_throttle_manager):
        """Test throttling integration."""
        from throttling import ThrottleType

        assert mock_throttle_manager.is_allowed(ThrottleType.POSTS_PER_HOUR)

        status = mock_throttle_manager.get_throttle_status(
            ThrottleType.POSTS_PER_HOUR
        )
        assert "type" in status
        assert "limit" in status
        assert "enabled" in status

    @pytest.mark.asyncio
    async def test_llm_orchestrator_integration(self, mock_llm_orchestrator):
        """Test LLM orchestrator integration."""
        health_status = await mock_llm_orchestrator.health_check_all()
        assert isinstance(health_status, dict)

        try:
            result = await mock_llm_orchestrator.generate_text("Test prompt")
            assert isinstance(result, str)
        except Exception as e:
            assert "No LLM providers available" in str(e) or "Mock provider" in str(e)
