#!/bin/bash

# Fetch the latest Git tag (from your incremental tag script)
LATEST_TAG=$(git describe --tags --abbrev=0)

# If no tag exists, start with an initial version, e.g., "1.0.0"
if [ -z "$LATEST_TAG" ]; then
  NEW_TAG="1.0.0"
else
  # Extract the major, minor, and patch numbers from the latest tag
  MAJOR=$(echo $LATEST_TAG | cut -d '.' -f 1)
  MINOR=$(echo $LATEST_TAG | cut -d '.' -f 2)
  PATCH=$(echo $LATEST_TAG | cut -d '.' -f 3)

  # Increment the patch number
  PATCH=$((PATCH + 1))

  # Create the new tag
  NEW_TAG="$MAJOR.$MINOR.$PATCH"
fi

# Define your Docker Hub image name
IMAGE_NAME="n8nhackers/agent"

# Build the Docker image and tag it with the new Git tag
docker build -t $IMAGE_NAME:$NEW_TAG .

# Push the image to Docker Hub
docker push $IMAGE_NAME:$NEW_TAG

# Optionally, tag the image as 'latest' too and push that
docker tag $IMAGE_NAME:$NEW_TAG $IMAGE_NAME:latest
docker push $IMAGE_NAME:latest

echo "Docker image tagged with '$NEW_TAG' and pushed to Docker Hub."
