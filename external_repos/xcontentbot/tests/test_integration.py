#!/usr/bin/env python3
"""
Integration tests for xcontentbot systems working together.
Tests the complete flow with error handling, circuit breakers, and observability.

This module re-exports from the integration test package for backwards compatibility.
"""

# Re-export all test classes for backwards compatibility
from tests.integration.test_system_flow import TestSystemIntegration
from tests.integration.test_error_flow import TestErrorHandlingFlow
from tests.integration.test_observability import TestObservabilityIntegration
from tests.integration.test_slow import TestSlowIntegration

__all__ = [
    "TestSystemIntegration",
    "TestErrorHandlingFlow",
    "TestObservabilityIntegration",
    "TestSlowIntegration",
]
