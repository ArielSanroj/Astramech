#!/usr/bin/env python3
"""
Integration tests for observability and metrics.
"""

import pytest
import asyncio
from pathlib import Path
import json


@pytest.mark.integration
class TestObservabilityIntegration:
    """Test observability metrics collection and export."""

    @pytest.mark.asyncio
    async def test_observability_metrics(self, mock_observability):
        """Test observability metrics collection."""
        mock_observability.metrics_collector.increment_counter("test.counter", 5)
        mock_observability.metrics_collector.set_gauge("test.gauge", 42.5)
        mock_observability.metrics_collector.record_timer("test.timer", 1.5)

        metrics = mock_observability.metrics_collector.get_metrics_summary()

        assert "test.counter" in metrics["counters"]
        assert metrics["counters"]["test.counter"] == 5

        assert "test.gauge" in metrics["gauges"]
        assert metrics["gauges"]["test.gauge"] == 42.5

        assert "test.timer" in metrics["timers"]
        assert metrics["timers"]["test.timer"]["count"] == 1
        assert metrics["timers"]["test.timer"]["avg"] == 1.5

    @pytest.mark.asyncio
    async def test_health_check_integration(self, mock_observability):
        """Test health check integration."""
        health_status = mock_observability.get_health_status()

        assert "status" in health_status
        assert "timestamp" in health_status
        assert "metrics" in health_status
        assert health_status["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mock_observability):
        """Test concurrent operations with observability."""
        async def process_post(post_id: str, delay: float = 0.1):
            metrics = mock_observability.start_post_processing(post_id, "test")
            await asyncio.sleep(delay)
            mock_observability.end_post_processing(post_id, "success")
            return post_id

        tasks = [process_post(f"post_{i}", 0.1) for i in range(5)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        assert all(result.startswith("post_") for result in results)

        health_status = mock_observability.get_health_status()
        assert "metrics" in health_status

    @pytest.mark.asyncio
    async def test_metrics_export(self, mock_observability, temp_dir):
        """Test metrics export functionality."""
        mock_observability.metrics_collector.increment_counter("test.export", 1)
        mock_observability.metrics_collector.set_gauge("test.gauge", 100.0)

        export_file = temp_dir / "test_metrics.json"
        result_file = mock_observability.export_metrics(str(export_file))

        assert Path(result_file).exists()

        with open(result_file, 'r') as f:
            exported_data = json.load(f)

        assert "timestamp" in exported_data
        assert "metrics" in exported_data
        assert "test.export" in exported_data["metrics"]["counters"]
