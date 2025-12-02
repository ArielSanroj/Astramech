#!/bin/bash
# Setup script for local development environment

set -e

echo "🚀 Setting up Astramech local development environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env and add your API keys (especially ALEGRA_EMAIL and ALEGRA_TOKEN)"
    else
        echo "❌ .env.example not found. Creating basic .env..."
        cat > .env << EOF
# Astramech Environment Variables
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://astramech:secret@postgres:5432/astramech
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
REDIS_URL=redis://redis:6379/0
FINANCE_SERVICE_URL=http://finance-supervincent:8000
ALEGRA_EMAIL=your_email@example.com
ALEGRA_TOKEN=your_token_here
POSTGRES_PASSWORD=secret
EOF
        echo "⚠️  Please edit .env and add your API keys"
    fi
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p external_repos/supervincent/uploads
mkdir -p logs
mkdir -p data

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Pull images
echo "📥 Pulling Docker images..."
docker compose pull

# Build services
echo "🔨 Building Docker services..."
docker compose build

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Start services: docker compose up -d"
echo "3. Check logs: docker compose logs -f"
echo "4. Run verification: python scripts/verify_finance_integration.py"

