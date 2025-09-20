#!/bin/bash

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
until curl -s http://localhost:4566/_localstack/health | grep -q '"s3": "available"'; do
  echo "Waiting for LocalStack..."
  sleep 2
done

echo "LocalStack is ready! Setting up AWS resources..."

# Create S3 bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://weather-data-bucket

# Create DynamoDB table
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
    --table-name weather-cache \
    --attribute-definitions \
        AttributeName=city,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=city,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

echo "AWS resources created successfully!"
echo "S3 bucket: weather-data-bucket"
echo "DynamoDB table: weather-cache"
