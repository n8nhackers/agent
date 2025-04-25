#!/bin/bash

# Fetch the latest Git tag (from your incremental tag script)
LATEST_TAG=$(git describe --tags --abbrev=0)

# If no tag exists, start with an initial version, e.g., "1.0.0"
if [ -z "$LATEST_TAG" ]; then
    LATEST_TAG="1.0.0"
fi

# Define your Docker Hub image name
IMAGE_NAME="n8nhackers/agent"

# Build the Docker image and tag it with the latest Git tag
docker build -t $IMAGE_NAME:$LATEST_TAG .

# Push the image to Docker Hub
docker push $IMAGE_NAME:$LATEST_TAG

# Tag the image as 'latest' too and push that
docker tag $IMAGE_NAME:$LATEST_TAG $IMAGE_NAME:latest
docker push $IMAGE_NAME:latest

echo "Docker image tagged with '$LATEST_TAG' and pushed to Docker Hub."
