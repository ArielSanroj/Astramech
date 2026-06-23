# xcontentbot - Intelligent X (Twitter) Engagement Bot

Automated bot for discovering and engaging with X posts about burnout, employee well-being, and productivity using AI-generated comments.

## Features

- 🔍 Smart search for relevant X posts
- 🤖 AI-powered comment generation (OpenAI GPT, Anthropic Claude)
- 🛡️ Circuit breakers and rate limiting
- 📊 Comprehensive monitoring and observability
- 🔄 Automatic retry with exponential backoff
- 🎯 Intelligent throttling to respect platform limits
- 💾 Persistent storage with SQLite/PostgreSQL
- 🚀 High-performance caching system
- 🔒 Security-first design with input validation

## Requirements

- Python 3.11+
- Playwright
- OpenAI API key or Anthropic API key
- X (Twitter) account

## Quick Start

1. **Clone and install:**
```bash
git clone <repo>
cd xcontentbot
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

2. **Configure environment:**
```bash
cp env.example .env
# Edit .env with your credentials
```

3. **Setup X session (one-time):**
```bash
# Uncomment line in x_mcp.py and run:
python x_mcp.py
# Then comment it back
```

4. **Run the bot:**
```bash
# Start MCP server
python x_mcp.py &

# Run bot
python x_client.py
```

## Configuration

See `bot_config_example.yaml` for all configuration options.

### Key Configuration Options

- **LLM Providers**: Configure OpenAI, Anthropic, or custom providers
- **Rate Limiting**: Adjust request throttling and delays
- **Circuit Breakers**: Set failure thresholds and recovery timeouts
- **Monitoring**: Enable metrics collection and health checks
- **Security**: Configure CORS origins and input validation

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m playwright
```

## Monitoring

Access monitoring dashboard at http://localhost:8080/dashboard

### Available Endpoints

- `GET /health` - System health status
- `GET /metrics` - Application metrics
- `GET /status` - Detailed system status
- `GET /config` - Current configuration
- `GET /logs` - Recent log entries
- `GET /dashboard` - Web dashboard

## Architecture

### Core Components

- **x_client.py**: Main orchestrator and scheduling
- **x_mcp.py**: MCP server for X platform interaction
- **llm_orchestrator.py**: Multi-provider LLM management
- **circuit_breaker.py**: Resilience patterns
- **throttling.py**: Rate limiting and throttling
- **observability.py**: Monitoring and logging
- **cache_manager.py**: High-performance caching
- **database.py**: Persistent storage layer

### Data Flow

1. **Search**: Bot searches for posts matching configured queries
2. **Filter**: Posts are filtered and validated for relevance
3. **Process**: AI generates contextual comments
4. **Post**: Comments are submitted to X (if auto-posting enabled)
5. **Track**: All activities are logged and metrics collected

## Security Features

- **Input Validation**: All inputs are validated and sanitized
- **URL Validation**: Prevents LinkedIn injection attacks
- **Credential Protection**: Sensitive data is filtered from logs
- **CORS Configuration**: Configurable cross-origin policies
- **Rate Limiting**: Prevents abuse and respects platform limits

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run linting
make lint

# Run formatting
make format

# Run tests
make test
```

### Available Commands

```bash
make help          # Show available commands
make install       # Install dependencies
make test          # Run tests with coverage
make lint          # Run linters
make format        # Format code
make clean         # Clean cache files
make run           # Run the bot
```

## Deployment

### Production Considerations

1. **Database**: Use PostgreSQL for production
2. **Monitoring**: Enable Prometheus metrics export
3. **Security**: Configure proper CORS origins
4. **Scaling**: Use multiple bot instances with shared database
5. **Backup**: Regular database backups

### Environment Variables

```bash
# Required
X_USERNAME=your_username
X_PASSWORD=your_password
OPENAI_API_KEY=sk-...

# Optional
DATABASE_URL=postgresql://user:pass@host:port/db
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

## Troubleshooting

### Common Issues

1. **X Login Blocked**: X.com blocks automated login attempts
   - Solution: Use manual login session setup
   - See `x_mcp.py` for session management

2. **Rate Limiting**: Too many requests
   - Solution: Adjust throttling configuration
   - Increase delays between requests

3. **LLM Errors**: API key issues
   - Solution: Check API keys in `.env`
   - Verify provider configuration

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug output
python x_client.py --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT

## Support

For issues and questions:
- Check the troubleshooting section
- Review the test suite for examples
- Open an issue on GitHub
