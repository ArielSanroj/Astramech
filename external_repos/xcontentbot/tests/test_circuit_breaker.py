#!/usr/bin/env python3
"""
Tests for circuit breaker functionality.
"""

import pytest
import asyncio
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState, CircuitBreakerManager


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Test that circuit opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test", config)
        
        async def failing_func():
            raise Exception("Test failure")
        
        # Trigger failures
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_circuit_closes_after_successes(self):
        """Test that circuit closes after successful calls."""
        config = CircuitBreakerConfig(failure_threshold=2, success_threshold=2)
        breaker = CircuitBreaker("test", config)
        
        async def failing_func():
            raise Exception("Test failure")
        
        async def success_func():
            return "success"
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        import time
        time.sleep(config.recovery_timeout + 0.1)
        
        # Circuit should be half-open now
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Successful calls should close the circuit
        for _ in range(2):
            result = await breaker.call(success_func)
            assert result == "success"
        
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_metrics(self):
        """Test circuit breaker metrics."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker("test", config)
        
        async def failing_func():
            raise Exception("Test failure")
        
        async def success_func():
            return "success"
        
        # Test successful call
        result = await breaker.call(success_func)
        assert result == "success"
        
        # Test failing calls
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        metrics = breaker.get_metrics()
        assert metrics["total_calls"] == 3
        assert metrics["total_failures"] == 2
        assert metrics["total_successes"] == 1
        assert metrics["circuit_opens"] == 1
    
    @pytest.mark.asyncio
    async def test_circuit_timeout(self):
        """Test circuit breaker timeout."""
        config = CircuitBreakerConfig(timeout=0.1)
        breaker = CircuitBreaker("test", config)
        
        async def slow_func():
            await asyncio.sleep(0.2)  # Longer than timeout
            return "success"
        
        with pytest.raises(asyncio.TimeoutError):
            await breaker.call(slow_func)
    
    @pytest.mark.asyncio
    async def test_circuit_reset(self):
        """Test circuit breaker reset."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker("test", config)
        
        async def failing_func():
            raise Exception("Test failure")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Reset the circuit
        breaker.reset()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
    
    def test_circuit_breaker_manager(self):
        """Test circuit breaker manager."""
        manager = CircuitBreakerManager()
        
        # Get a circuit breaker
        breaker1 = manager.get_breaker("test1")
        breaker2 = manager.get_breaker("test2")
        breaker1_again = manager.get_breaker("test1")
        
        # Should return the same instance for same name
        assert breaker1 is breaker1_again
        assert breaker1 is not breaker2
        
        # Test metrics
        metrics = manager.get_all_metrics()
        assert "test1" in metrics
        assert "test2" in metrics
        
        # Test reset all
        manager.reset_all()
        assert breaker1.state == CircuitState.CLOSED
        assert breaker2.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_decorator(self):
        """Test circuit breaker decorator."""
        from circuit_breaker import circuit_breaker
        
        config = CircuitBreakerConfig(failure_threshold=2)
        
        @circuit_breaker("decorator_test", config)
        async def failing_function():
            raise Exception("Decorator test failure")
        
        # Should fail and open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await failing_function()
        
        # Circuit should be open
        from circuit_breaker import circuit_manager
        breaker = circuit_manager.get_breaker("decorator_test")
        assert breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_retry_with_circuit_breaker(self):
        """Test retry with circuit breaker."""
        from circuit_breaker import RetryWithCircuitBreaker
        
        retry_breaker = RetryWithCircuitBreaker(
            circuit_breaker_name="retry_test",
            max_retries=2,
            base_delay=0.01
        )
        
        call_count = 0
        
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Flaky function failure")
            return "success"
        
        # Should succeed after retries
        result = await retry_breaker.call(flaky_function)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_state(self):
        """Test circuit breaker half-open state behavior."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,
            success_threshold=2
        )
        breaker = CircuitBreaker("test", config)
        
        async def failing_func():
            raise Exception("Test failure")
        
        async def success_func():
            return "success"
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery
        await asyncio.sleep(0.2)
        
        # Should be half-open
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Any failure in half-open should open circuit again
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
