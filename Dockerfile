# Multi-stage build: Node.js stage for frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend files
COPY frontend/package*.json ./

# Install ALL dependencies (including dev dependencies for build)
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Python stage for backend
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    openssh-client \
    sshpass \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Copy built frontend files from Node.js stage
COPY --from=frontend-builder /frontend/dist/* /app/static/js/network-workflow/

# Create necessary directories with proper permissions
RUN mkdir -p static media logs staticfiles && \
    chmod 755 static media logs staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]