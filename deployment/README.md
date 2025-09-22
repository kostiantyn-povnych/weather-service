# Weather Service Deployment

This directory contains Docker Compose configuration for running the Weather Service with LocalStack for AWS services simulation.

## Services

- **weather-service**: The FastAPI application
- **localstack**: AWS services simulation (S3, DynamoDB)

## Quick Start

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenWeatherMap API key:
   ```
   OPENWEATHERMAP_API_KEY=your_api_key_here
   ```

3. Start the services:
   ```bash
   cd deployment
   docker-compose up -d
   ```

4. Initialize LocalStack resources (optional):
   ```bash
   ./init-localstack.sh
   ```

## Access Points

- **Weather Service API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **LocalStack**: http://localhost:4566

## Environment Variables

- `OPENWEATHERMAP_API_KEY`: Required for weather data from OpenWeatherMap
- `AWS_ACCESS_KEY_ID`: Set to "test" for LocalStack
- `AWS_SECRET_ACCESS_KEY`: Set to "test" for LocalStack
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)
- `AWS_ENDPOINT_URL`: LocalStack endpoint (http://localstack:4566)

## LocalStack Resources

The initialization script creates:
- S3 bucket: `weather-data-bucket`
- DynamoDB table: `weather-cache` (with city and timestamp keys)

## Development

To rebuild the weather service after code changes:
```bash
docker-compose up --build weather-service
```

To view logs:
```bash
docker-compose logs -f weather-service
docker-compose logs -f localstack
```
