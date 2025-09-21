# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY requirements.lock ./
COPY README.md ./
COPY config/logging.yml ./config/logging.yml

RUN pip install --no-cache-dir -r requirements.lock

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "weather_service.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "config/logging.yml"]
