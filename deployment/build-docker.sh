#!/bin/bash

# Weather Service Docker Build Script
# This script builds the Docker image for the weather service

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="weather-service"
TAG="latest"
BUILD_CONTEXT="."
DOCKERFILE="deployment/Dockerfile"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME     Docker image name (default: weather-service)"
    echo "  -t, --tag TAG       Docker image tag (default: latest)"
    echo "  -c, --context PATH  Build context path (default: .)"
    echo "  -f, --file FILE     Dockerfile path (default: deployment/Dockerfile)"
    echo "  --no-cache          Build without using cache"
    echo "  --push              Push image to registry after building"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build with defaults"
    echo "  $0 -n my-weather -t v1.0.0          # Custom name and tag"
    echo "  $0 --no-cache                        # Build without cache"
    echo "  $0 --push                            # Build and push"
}

# Parse command line arguments
NO_CACHE=""
PUSH_IMAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -c|--context)
            BUILD_CONTEXT="$2"
            shift 2
            ;;
        -f|--file)
            DOCKERFILE="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate inputs
if [[ ! -f "$BUILD_CONTEXT/$DOCKERFILE" ]]; then
    print_error "Dockerfile not found: $BUILD_CONTEXT/$DOCKERFILE"
    exit 1
fi

if [[ ! -f "$BUILD_CONTEXT/pyproject.toml" ]]; then
    print_error "pyproject.toml not found in build context: $BUILD_CONTEXT"
    exit 1
fi

# Full image name
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

print_info "Building Docker image: $FULL_IMAGE_NAME"
print_info "Build context: $BUILD_CONTEXT"
print_info "Dockerfile: $DOCKERFILE"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running or not accessible"
    exit 1
fi

# Build the image
print_info "Starting Docker build..."
BUILD_CMD="docker build $NO_CACHE -t $FULL_IMAGE_NAME -f $DOCKERFILE $BUILD_CONTEXT"

if [[ -n "$NO_CACHE" ]]; then
    print_warning "Building without cache (this may take longer)"
fi

echo "Executing: $BUILD_CMD"
if $BUILD_CMD; then
    print_success "Docker image built successfully: $FULL_IMAGE_NAME"
else
    print_error "Docker build failed"
    exit 1
fi

# Show image information
print_info "Image details:"
docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Push image if requested
if [[ "$PUSH_IMAGE" == true ]]; then
    print_info "Pushing image to registry..."
    if docker push "$FULL_IMAGE_NAME"; then
        print_success "Image pushed successfully: $FULL_IMAGE_NAME"
    else
        print_error "Failed to push image"
        exit 1
    fi
fi

print_success "Build process completed!"
print_info "To run the container: docker run -p 8000:8000 $FULL_IMAGE_NAME"
print_info "To run with docker-compose: cd deployment && docker-compose up --build"
