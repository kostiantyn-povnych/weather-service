# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rye
RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
ENV PATH="/root/.rye/shims:$PATH"

# Copy project files
COPY pyproject.toml ./
COPY requirements.lock ./

# Install dependencies
RUN rye sync --no-dev

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
