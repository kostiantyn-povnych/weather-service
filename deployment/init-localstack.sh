#!/usr/bin/env bash
set -euo pipefail

AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localstack:4566}"
AWS_REGION="${AWS_DEFAULT_REGION:-us-east-1}"

BUCKET_NAME="${DATA_STORE_S3_BUCKET_NAME:-weather-svc-data}"
TABLE_NAME="${EVENT_STORE_AWS_DYNAMODB_TABLE_NAME:-weather-svc-events}"

echo "Waiting for LocalStack to be ready at ${AWS_ENDPOINT_URL} ..."
# LocalStack health sometimes returns partials; wait for overall ready + s3/dynamodb available
until curl -fsS "${AWS_ENDPOINT_URL}/_localstack/health" | grep -q '"s3": "available"'; do
  echo "  ... still waiting (s3 not available yet)"
  sleep 2
done
until curl -fsS "${AWS_ENDPOINT_URL}/_localstack/health" | grep -q '"dynamodb": "available"'; do
  echo "  ... still waiting (dynamodb not available yet)"
  sleep 2
done
echo "LocalStack is ready."

echo "Ensuring S3 bucket exists: ${BUCKET_NAME}"
if aws --endpoint-url="${AWS_ENDPOINT_URL}" --region "${AWS_REGION}" s3api head-bucket --bucket "${BUCKET_NAME}" 2>/dev/null; then
  echo "  Bucket already exists."
else
  aws --endpoint-url="${AWS_ENDPOINT_URL}" --region "${AWS_REGION}" s3api create-bucket \
    --bucket "${BUCKET_NAME}" \
    --create-bucket-configuration LocationConstraint="${AWS_REGION}" || {
      # LocalStack S3 may ignore LocationConstraint; try plain s3 mb
      aws --endpoint-url="${AWS_ENDPOINT_URL}" --region "${AWS_REGION}" s3 mb "s3://${BUCKET_NAME}" || true
    }
  echo "  Bucket created (or already present)."
fi

echo "Ensuring DynamoDB table exists: ${TABLE_NAME}"
if aws --endpoint-url="${AWS_ENDPOINT_URL}" --region "${AWS_REGION}" dynamodb describe-table --table-name "${TABLE_NAME}" >/dev/null 2>&1; then
  echo "  Table already exists."
else
  aws --endpoint-url="${AWS_ENDPOINT_URL}" --region "${AWS_REGION}" dynamodb create-table \
    --table-name "${TABLE_NAME}" \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
  echo "  Waiting for table to be active..."
  aws --endpoint-url="${AWS_ENDPOINT_URL}" --region "${AWS_REGION}" dynamodb wait table-exists --table-name "${TABLE_NAME}"
  echo "  Table is active."
fi

echo "Initialization complete."
echo "S3 bucket: ${BUCKET_NAME}"
echo "DynamoDB table: ${TABLE_NAME}"
