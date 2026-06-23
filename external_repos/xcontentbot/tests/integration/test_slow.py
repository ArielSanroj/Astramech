#!/usr/bin/env python3
"""
Slow integration tests that may take longer to run.
"""

import pytest
import asyncio
import time


@pytest.mark.integration
@pytest.mark.slow
class TestSlowIntegration:
    """Slow integration tests that may take longer to run."""

    @pytest.mark.asyncio
    async def test_long_running_operations(self, mock_observability):
        """Test long-running operations with observability."""
        start_time = time.time()

        async def long_operation():
            await asyncio.sleep(1.0)
            return "completed"

        result = await long_operation()

        assert result == "completed"
        assert time.time() - start_time >= 1.0

        post_id = "long_running_post"
        metrics = mock_observability.start_post_processing(post_id, "long_test")

        await long_operation()

        mock_observability.end_post_processing(post_id, "success")

        health_status = mock_observability.get_health_status()
        assert "metrics" in health_status

    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, mock_observability):
        """Test memory usage monitoring over time."""
        data_structures = []

        for i in range(100):
            data_structures.append([f"data_{j}" for j in range(1000)])

            system_metrics = mock_observability.system_metrics.get_system_metrics()
            memory_percent = system_metrics.get("memory", {}).get("percent", 0)

            mock_observability.metrics_collector.set_gauge(
                "memory.usage", memory_percent
            )

        metrics = mock_observability.metrics_collector.get_metrics_summary()
        assert "memory.usage" in metrics["gauges"]

        del data_structures
