# Weather Service

A FastAPI-based weather service that provides current weather information for cities worldwide.

## Features

- **Weather Service**: Get current weather data for any city using OpenWeatherMap API
- **Geolocation Service**: Resolve city names to coordinates using OpenWeatherMap Geocoding API
- **Caching**: Redis-based caching to reduce API calls and improve performance
- **Rate Limiting**: Configurable rate limiting to prevent API abuse
- **Data Storage**: Support for both local file storage and AWS S3
- **Event Logging**: Track API usage with DynamoDB or local file logging

## Data Providers

This service uses **OpenWeatherMap** as the primary data provider for both weather and geolocation services:

- **Weather Data**: Current weather conditions, temperature, humidity, and more via OpenWeatherMap Current Weather API
- **Geolocation**: City name resolution to coordinates via OpenWeatherMap Geocoding API
- **API Key Required**: You'll need a free OpenWeatherMap API key to use this service

## Quick Start

### Docker Build & Run

Build the Docker image:

```bash
./deployment/build-docker.sh
```

Run with Docker Compose (includes LocalStack for AWS services simulation):

```bash
# Create environment file from example
cp .env.example.local .env  # For local development
# OR
cp .env.example.aws-localstack-full .env  # For full AWS simulation

# Edit .env and add your OpenWeatherMap API key
# Replace 'your_openweathermap_api_key_here' with your actual API key

# Start all services
docker-compose up --build
```

The service will be available at `http://localhost:8000`

### Environment Configuration

The project includes two example environment files:

- **`.env.example.local`**: Minimal setup for local development

  - Uses local file storage and memory caching
  - Rate limiting disabled
  - Perfect for development and testing

- **`.env.example.aws-localstack-full`**: Full AWS simulation with LocalStack
  - Uses S3 for data storage and DynamoDB for events
  - Redis-based caching and rate limiting
  - Simulates production AWS environment locally

**Required Setup:**

1. Copy one of the example files to `.env`
2. Edit `.env` and replace `your_openweathermap_api_key_here` with your actual OpenWeatherMap API key
3. Run `docker-compose up --build`

### LocalStack Setup

The Docker Compose setup includes LocalStack for AWS services simulation:

**Services:**

- **Weather Service**: FastAPI application (port 8000)
- **LocalStack**: AWS services simulation (port 4566)
- **Redis**: Caching and rate limiting backend (port 6379)

**LocalStack Resources (auto-created):**

- **S3 Bucket**: `weather-svc-data` - for weather data storage
- **DynamoDB Table**: `weather-svc-events` - for API usage event logging

**Access Points:**

- Weather Service API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- LocalStack Dashboard: `http://localhost:4566`

**Initialization:**
LocalStack resources are automatically created when the services start. The `init-localstack.sh` script ensures S3 buckets and DynamoDB tables are properly configured.

### Development Setup

This project uses [Rye](https://rye.astral.sh/) as the package manager:

```bash
# Install Rye
curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash

# Install dependencies
rye sync

# Run development server
uvicorn weather_service.api.app:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

Get weather for a city:

```bash
curl "http://localhost:8000/api/v1/weather?city=London&country_code=GB"
```

API documentation available at: `http://localhost:8000/docs`

## Environment Variables

Environment variables are configured via `.env` files. Copy one of the example files:

- `.env.example.local` - for local development
- `.env.example.aws-localstack-full` - for full AWS simulation

**Required:**

- `OPENWEATHERMAP_API_KEY`: Your OpenWeatherMap API key (get a free key at [openweathermap.org](https://openweathermap.org/api))

**Optional (see example files for full configuration):**

- `CACHE_ENABLED`: Enable/disable caching (default: true)
- `RATE_LIMIT_ENABLED`: Enable/disable rate limiting (default: false)
- `DATA_STORE_TYPE`: Storage backend (local/aws_s3)
- `EVENT_STORE_TYPE`: Event logging backend (local/aws_dynamodb)

## CI/CD Setup

GitHub Actions CI (the integration tests in particular) expects the following repository secret to be present: `OPENWEATHERMAP_API_KEY`
