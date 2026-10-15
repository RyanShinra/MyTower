# MyTower Server Dockerfile
# Multi-stage build for smaller final image

# ============================================================================
# Stage 1: Builder (installs dependencies)
# ============================================================================
FROM python:3.13-slim AS builder

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the lock file first (for layer caching)
# The lock file is self-contained (it already includes everything from
# requirements-base.txt) and pins exact versions, so every build resolves
# the same dependency set. Regenerate it per the header in the file.
COPY requirements-server.lock ./

# Install Python dependencies (server only, no pygame!)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-server.lock

# ============================================================================
# Stage 2: Runtime (lean production image)
# ============================================================================
FROM python:3.13-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mytower

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY mytower/ /app/mytower/

# Create logs directory (writable by non-root user)
RUN mkdir -p /app/logs && chown -R mytower:mytower /app

# Switch to non-root user
USER mytower

# Expose port (configurable via environment)
EXPOSE 8000

# Health check for AWS load balancer
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1 \
    MYTOWER_MODE=headless \
    MYTOWER_PORT=8000 \
    MYTOWER_LOG_LEVEL=INFO

# Run the application (server mode = headless in code)
CMD ["python", "-m", "mytower.main", \
     "--with-graphql", "--headless", \
     "--demo", \
     "--port", "8000", \
     "--log-level", "INFO"]
