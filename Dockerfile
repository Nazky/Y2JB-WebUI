# Use official Python 3.14 slim image (lightweight, security-hardened)
FROM python:3.14-slim-bookworm

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports (8000 = WebUI, 53 = DNS)
EXPOSE 8000 53/udp

# Start the application
CMD ["python", "server.py"]
