FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Note: shared/events will be available via volume mount or PYTHONPATH
# The app.py uses sys.path to locate shared modules

# Expose port (if needed for health checks)
EXPOSE 8080

# Run orchestrator
CMD ["python", "app.py"]
