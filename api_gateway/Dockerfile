FROM python:3.11-slim
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH to include current directory
ENV PYTHONPATH=/app

EXPOSE 8000

# Use python -m uvicorn to ensure proper module resolution
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
