#!/usr/bin/env python3
"""
Pytest configuration and fixtures for xcontentbot tests.
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import ConfigurationManager
from observability import ObservabilityManager
from circuit_breaker import CircuitBreakerManager
from throttling import ThrottleManager
from llm_orchestrator import LLMOrchestrator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config_manager(temp_dir):
    """Create a mock configuration manager."""
    config_file = temp_dir / "test_config.yaml"
    
    # Create test configuration
    test_config = {
        "app": {
            "queries": ["test query"],
            "limit": 5,
            "max_posts_to_process": 2,
            "auto_post": False,
            "mcp_server_url": "http://localhost:8000/mcp"
        },
        "llm": {
            "providers": {
                "mock": {
                    "name": "mock",
                    "model": "test-model",
                    "api_key_env": "TEST_API_KEY",
                    "temperature": 0.4,
                    "max_tokens": 100
                }
            },
            "default_provider": "mock"
        },
        "retry": {
            "max_retries": 2,
            "base_delay": 0.1,
            "max_delay": 1.0
        },
        "circuit_breaker": {
            "failure_threshold": 3,
            "recovery_timeout": 10.0
        },
        "rate_limit": {
            "posts_per_hour": 10,
            "posts_per_day": 50
        }
    }
    
    import yaml
    with open(config_file, 'w') as f:
        yaml.dump(test_config, f)
    
    # Set environment variable
    os.environ["CONFIG_FILE"] = str(config_file)
    
    config_manager = ConfigurationManager(str(config_file))
    yield config_manager


@pytest.fixture
def mock_observability(temp_dir):
    """Create a mock observability manager."""
    log_file = temp_dir / "test.log"
    observability = ObservabilityManager(str(log_file))
    yield observability


@pytest.fixture
def mock_circuit_breaker_manager():
    """Create a mock circuit breaker manager."""
    return CircuitBreakerManager()


@pytest.fixture
def mock_throttle_manager():
    """Create a mock throttle manager."""
    return ThrottleManager()


@pytest.fixture
def mock_llm_orchestrator():
    """Create a mock LLM orchestrator."""
    return LLMOrchestrator()


@pytest.fixture
def mock_playwright_page():
    """Create a mock Playwright page."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.locator = MagicMock()
    page.route = AsyncMock()
    page.click = AsyncMock()
    page.fill = AsyncMock()
    page.type = AsyncMock()
    page.is_visible = AsyncMock(return_value=True)
    page.wait_for_selector = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    return page


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx client."""
    client = AsyncMock()
    
    # Mock successful responses
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.raise_for_status = MagicMock()
    
    client.get.return_value = mock_response
    client.post.return_value = mock_response
    
    return client


@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    return {
        "id": "test_post_123",
        "url": "https://x.com/testuser/status/123456789",
        "author": "testuser",
        "text": "This is a test post about burnout and productivity",
        "text_preview": "This is a test post about burnout..."
    }


@pytest.fixture
def sample_search_response():
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


@pytest.fixture
def mock_environment():
    """Set up mock environment variables."""
    env_vars = {
        "X_USERNAME": "testuser",
        "X_PASSWORD": "testpass",
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "LOG_LEVEL": "DEBUG",
        "AUTO_POST": "false"
    }
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
    
    yield env_vars
    
    # Clean up
    for key in env_vars.keys():
        os.environ.pop(key, None)


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "playwright: marks tests that require Playwright"
    )
    config.addinivalue_line(
        "markers", "llm: marks tests that require LLM providers"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )