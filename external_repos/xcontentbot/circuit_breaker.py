#!/usr/bin/env python3
"""
Circuit Breaker implementation for resilient API calls and Playwright operations.
Provides automatic failure detection and recovery mechanisms.
"""

import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import functools

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: float = 60.0      # Seconds to wait before half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 30.0               # Timeout for individual calls
    expected_exception: tuple = (Exception,)  # Exceptions that count as failures


class CircuitBreaker:
    """
    Circuit breaker implementation for resilient operations.
    
    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Circuit is open, calls fail immediately
    - HALF_OPEN: Testing if service recovered, limited calls allowed
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # Metrics
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.circuit_opens = 0
        self.circuit_closes = 0
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.success_count += 1
        self.total_successes += 1
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._open_circuit()
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state opens the circuit
            self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit."""
        self.state = CircuitState.OPEN
        self.circuit_opens += 1
        self.success_count = 0
        logger.warning(f"Circuit breaker '{self.name}' opened due to {self.failure_count} failures")
    
    def _close_circuit(self):
        """Close the circuit."""
        self.state = CircuitState.CLOSED
        self.circuit_closes += 1
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' closed - service recovered")
    
    def _half_open_circuit(self):
        """Move circuit to half-open state."""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' moved to half-open state")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenException: When circuit is open
            Exception: When function fails
        """
        self.total_calls += 1
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._half_open_circuit()
            else:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Last failure: {self.last_failure_time}"
                )
        
        # Execute function with timeout
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            self._on_success()
            return result
            
        except asyncio.TimeoutError:
            self._on_failure()
            raise TimeoutError(f"Circuit breaker '{self.name}' call timed out")
            
        except self.config.expected_exception as e:
            self._on_failure()
            logger.warning(f"Circuit breaker '{self.name}' caught expected exception: {e}")
            raise
            
        except Exception as e:
            # Unexpected exception - still count as failure
            self._on_failure()
            logger.error(f"Circuit breaker '{self.name}' caught unexpected exception: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "circuit_opens": self.circuit_opens,
            "circuit_closes": self.circuit_closes,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "failure_rate": self.total_failures / max(self.total_calls, 1),
            "success_rate": self.total_successes / max(self.total_calls, 1)
        }
    
    def reset(self):
        """Reset circuit breaker to initial state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        logger.info(f"Circuit breaker '{self.name}' reset")


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerManager:
    """Manages multiple circuit breakers."""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(name, config)
        return self.breakers[name]
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers."""
        return {name: breaker.get_metrics() for name, breaker in self.breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset()


# Global circuit breaker manager
circuit_manager = CircuitBreakerManager()


def circuit_breaker(name: str, config: CircuitBreakerConfig = None):
    """
    Decorator for applying circuit breaker to functions.
    
    Usage:
        @circuit_breaker("api_call", CircuitBreakerConfig(failure_threshold=3))
        async def api_call():
            # function implementation
    """
    def decorator(func):
        breaker = circuit_manager.get_breaker(name, config)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator


class RetryWithCircuitBreaker:
    """
    Combines retry logic with circuit breaker for maximum resilience.
    """
    
    def __init__(self, 
                 circuit_breaker_name: str,
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: float = 0.1,
                 circuit_config: CircuitBreakerConfig = None):
        self.circuit_breaker_name = circuit_breaker_name
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.circuit_config = circuit_config or CircuitBreakerConfig()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry and circuit breaker protection.
        """
        breaker = circuit_manager.get_breaker(self.circuit_breaker_name, self.circuit_config)
        
        for attempt in range(self.max_retries + 1):
            try:
                return await breaker.call(func, *args, **kwargs)
            except CircuitBreakerOpenException:
                # Circuit is open, don't retry
                raise
            except Exception as e:
                if attempt == self.max_retries:
                    # Last attempt failed
                    raise
                
                # Calculate delay with exponential backoff and jitter
                delay = min(
                    self.base_delay * (self.exponential_base ** attempt),
                    self.max_delay
                )
                jitter_amount = delay * self.jitter * (0.5 - asyncio.get_event_loop().time() % 1)
                delay += jitter_amount
                
                logger.warning(
                    f"Retry attempt {attempt + 1}/{self.max_retries} for {self.circuit_breaker_name} "
                    f"after {type(e).__name__}: {e}. Retrying in {delay:.2f}s"
                )
                await asyncio.sleep(delay)


# Predefined circuit breaker configurations for common use cases
API_CALL_CONFIG = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=30.0,
    success_threshold=3,
    timeout=30.0,
    expected_exception=(Exception,)
)

PLAYWRIGHT_CONFIG = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=60.0,
    success_threshold=2,
    timeout=60.0,
    expected_exception=(Exception,)
)

LLM_CALL_CONFIG = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=120.0,
    success_threshold=2,
    timeout=120.0,
    expected_exception=(Exception,)
)