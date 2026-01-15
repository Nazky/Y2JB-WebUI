# Use official Python 3.11 slim image (lightweight, security-hardened)
FROM python:3.11.9-slim-bookworm

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Security hardening: never run as root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port 8000
EXPOSE 8000

# Start the application
CMD ["python", "server.py"]
