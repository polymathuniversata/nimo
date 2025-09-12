# Multi-stage build for optimized production image
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash nimo

# Set work directory
WORKDIR /app

# Install Python dependencies in a virtual environment
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy virtual environment from dependencies stage
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs instance metta_state && \
    chown -R nimo:nimo /app

# Switch to non-root user
USER nimo

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health/live || exit 1

# Expose port
EXPOSE 5000

# Start application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "app:create_app()"]
