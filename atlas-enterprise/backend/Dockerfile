# ATLAS Enterprise Backend Dockerfile
# Multi-stage build for optimized production image

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY simple_requirements.txt .
RUN pip install -r simple_requirements.txt

# Copy application code
COPY . .
# Copy data directory
COPY data/ ./data/

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Command for development
CMD ["uvicorn", "main_unified:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Create non-root user
RUN useradd --create-home --shell /bin/bash atlas

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY simple_requirements.txt .
RUN pip install -r simple_requirements.txt

# Copy application code
COPY . .
# Copy data directory
COPY data/ ./data/

# Create uploads directory and set permissions
RUN mkdir -p uploads && chown -R atlas:atlas /app

# Switch to non-root user
USER atlas

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command for production
CMD ["uvicorn", "main_unified:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 