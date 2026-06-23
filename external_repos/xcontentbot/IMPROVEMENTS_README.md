# xcontentbot Improvements

This document outlines the comprehensive improvements made to xcontentbot, focusing on automated testing, error handling, observability, and system resilience.

## 🧪 Automated Testing & Regression Detection

### Test Suite Structure
```
tests/
├── __init__.py
├── conftest.py                    # Pytest configuration and fixtures
├── test_playwright_selectors.py   # Playwright selector tests
├── test_integration.py            # Integration tests
└── test_circuit_breaker.py        # Circuit breaker tests
```

### Key Features
- **Selector Regression Detection**: Automated tests for Playwright selectors to catch changes early
- **Mock Testing**: Comprehensive mocks for Playwright, httpx, and LLM providers
- **Integration Tests**: End-to-end testing of the complete flow
- **Performance Testing**: Tests for response times and resource usage

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m "not slow"             # Exclude slow tests

# Run with coverage
pytest --cov=xcontentbot --cov-report=html
```

## 🔄 Circuit Breakers & Error Handling

### Circuit Breaker Implementation
- **Automatic Failure Detection**: Monitors API calls and Playwright operations
- **Recovery Mechanisms**: Automatic recovery testing when services are back
- **Configurable Thresholds**: Customizable failure thresholds and timeouts
- **Multiple Breakers**: Separate breakers for different service types

### Error Handling Features
- **Exponential Backoff**: Intelligent retry with exponential backoff
- **Jitter**: Prevents thundering herd problems
- **Timeout Management**: Configurable timeouts for all operations
- **Graceful Degradation**: System continues operating with reduced functionality

### Usage Example
```python
from circuit_breaker import circuit_breaker, API_CALL_CONFIG

@circuit_breaker("api_calls", API_CALL_CONFIG)
async def api_call():
    # Your API call here
    pass
```

## 📊 Structured Logging & Metrics

### Observability Features
- **Structured JSON Logging**: Machine-readable logs for better analysis
- **Comprehensive Metrics**: Counters, gauges, and timers for all operations
- **Performance Monitoring**: Response times, success rates, and error tracking
- **System Metrics**: Memory, CPU, and resource usage monitoring

### Metrics Collected
- **Post Processing**: Success/failure rates, processing times
- **API Calls**: Response times, error rates, retry counts
- **Selector Operations**: Failure rates, performance metrics
- **System Health**: Memory usage, CPU usage, uptime

### Usage Example
```python
from observability import observability, log_post_event

# Start tracking a post
metrics = observability.start_post_processing(post_id, query)

# Record events
log_post_event("processing_started", post_id, query=query)
observability.record_api_call(post_id, "submit_comment", True, 1.5)

# End tracking
observability.end_post_processing(post_id, "success")
```

## 🤖 Decoupled LLM Orchestration

### Multi-Provider Support
- **OpenAI GPT**: GPT-4, GPT-3.5-turbo, GPT-4o-mini
- **Anthropic Claude**: Claude-3-Haiku, Claude-3-Sonnet
- **Mock Provider**: For testing and development
- **Easy Extension**: Simple to add new providers

### Features
- **Automatic Fallback**: Falls back to secondary providers on failure
- **Load Balancing**: Distributes requests across healthy providers
- **Health Monitoring**: Continuous health checks for all providers
- **Configurable Parameters**: Temperature, max tokens, timeouts per provider

### Usage Example
```python
from llm_orchestrator import generate_comment, generate_text

# Generate a comment
comment = await generate_comment(
    post_text="Great insights on burnout!",
    author="username",
    provider="openai",  # Optional: specify provider
    temperature=0.4     # Optional: override temperature
)

# Generate text with custom parameters
text = await generate_text(
    "Write a professional comment",
    system_prompt="Be helpful and concise",
    max_tokens=100
)
```

## 🚦 Throttling & Rate Limiting

### Throttling Types
- **Posts per Hour/Day**: Prevents spam and respects platform limits
- **API Calls per Minute**: Protects against rate limiting
- **Login Attempts**: Prevents brute force attacks
- **Search Requests**: Manages search API usage

### Advanced Features
- **Token Bucket Algorithm**: Smooth rate limiting with burst capacity
- **Sliding Window**: Precise rate limiting for post operations
- **Adaptive Throttling**: Adjusts limits based on success rates
- **Burst Handling**: Allows temporary spikes in activity

### Usage Example
```python
from throttling import throttle_posts_per_hour, ThrottleException

@throttle_posts_per_hour(wait_on_throttle=True)
async def post_comment():
    # Your posting logic here
    pass
```

## ⚙️ Configuration Management

### Configuration Sources
1. **Default Values**: Sensible defaults for all settings
2. **YAML Files**: `bot_config.yaml` for persistent configuration
3. **Environment Variables**: Override any setting via env vars
4. **Runtime Updates**: Change configuration without restart

### Configuration Categories
- **Application Settings**: Queries, limits, auto-posting
- **LLM Configuration**: Providers, models, parameters
- **Retry Settings**: Backoff, timeouts, retry counts
- **Rate Limiting**: Posts per hour/day, API limits
- **Playwright Settings**: Headless mode, timeouts, viewport
- **Logging Configuration**: Levels, formats, file paths
- **Observability**: Metrics, health checks, exports

### Usage Example
```python
from config_manager import get_config, set_config, get_llm_provider

# Get configuration
queries = get_config("app.queries", ["burnout"])
max_retries = get_config("retry.max_retries", 3)

# Set configuration
set_config("app.auto_post", True)

# Get LLM provider configuration
provider_config = get_llm_provider("openai")
```

## 📈 Monitoring & Health Checks

### Health Check Endpoints
- **`/health`**: Overall system health status
- **`/metrics`**: Detailed metrics and statistics
- **`/status`**: Comprehensive system status
- **`/config`**: Current configuration
- **`/logs`**: Recent log entries
- **`/diagnostics`**: System diagnostics
- **`/dashboard`**: Web-based monitoring dashboard

### Health Status Levels
- **Healthy**: All systems operating normally
- **Degraded**: Some systems experiencing issues
- **Unhealthy**: Multiple systems failing
- **Critical**: System-wide failures

### Usage Example
```bash
# Start monitoring service
python -m monitoring

# Check health
curl http://localhost:8080/health

# View metrics
curl http://localhost:8080/metrics

# Access dashboard
open http://localhost:8080/dashboard
```

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure the System
```bash
# Copy example configuration
cp bot_config_example.yaml bot_config.yaml

# Edit configuration
nano bot_config.yaml
```

### 3. Set Environment Variables
```bash
export X_USERNAME="your_username"
export X_PASSWORD="your_password"
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

### 4. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xcontentbot --cov-report=html
```

### 5. Start the System
```bash
# Start MCP server
python x_mcp.py &

# Start monitoring
python -m monitoring &

# Run the bot
python x_client.py
```

## 🔧 Troubleshooting

### Common Issues

#### Circuit Breaker Open
```python
# Reset circuit breakers
from circuit_breaker import circuit_manager
circuit_manager.reset_all()
```

#### Throttling Issues
```python
# Check throttle status
from throttling import get_throttle_status
status = get_throttle_status()
print(status)
```

#### LLM Provider Failures
```python
# Check provider health
from llm_orchestrator import llm_orchestrator
health = await llm_orchestrator.health_check_all()
print(health)
```

#### Configuration Issues
```python
# Reload configuration
from config_manager import config_manager
config_manager.reload()
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python x_client.py --verbose
```

## 📚 API Reference

### Observability API
```python
# Start post processing tracking
metrics = observability.start_post_processing(post_id, query)

# Record events
observability.record_selector_failure(post_id, selector, error)
observability.record_api_call(post_id, endpoint, success, duration)
observability.record_login_attempt(success, duration)

# End tracking
observability.end_post_processing(post_id, status, error_message)

# Get health status
health = observability.get_health_status()

# Export metrics
observability.export_metrics("metrics.json")
```

### Circuit Breaker API
```python
# Create circuit breaker
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60.0)
breaker = CircuitBreaker("my_service", config)

# Use circuit breaker
result = await breaker.call(my_function, arg1, arg2)

# Get metrics
metrics = breaker.get_metrics()
```

### Throttling API
```python
# Check if request is allowed
from throttling import is_allowed, ThrottleType

if is_allowed(ThrottleType.POSTS_PER_HOUR):
    # Proceed with posting
    pass

# Wait if throttled
from throttling import wait_if_throttled
wait_time = wait_if_throttled(ThrottleType.POSTS_PER_HOUR)
```

## 🤝 Contributing

### Adding New Tests
1. Create test file in `tests/` directory
2. Use appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
3. Add fixtures for common test data
4. Include both positive and negative test cases

### Adding New Providers
1. Create provider class inheriting from `LLMProvider`
2. Implement `generate_text()` and `health_check()` methods
3. Add provider to `LLMOrchestrator._load_providers()`
4. Add configuration to `bot_config_example.yaml`

### Adding New Metrics
1. Use `observability.metrics_collector` for recording metrics
2. Add appropriate tags for filtering and grouping
3. Update health check logic if needed
4. Document new metrics in this README

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Playwright team for excellent browser automation
- FastAPI team for the web framework
- OpenAI and Anthropic for LLM APIs
- The open-source community for inspiration and tools