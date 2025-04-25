#!/bin/bash

# Fetch the latest tag
LATEST_TAG=$(git describe --tags --abbrev=0)

# Check if a tag exists
if [ -z "$LATEST_TAG" ]; then
  # If no tag exists, start with an initial version, e.g., "1.0.0"
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

# Create the new tag
git tag -a "$NEW_TAG" -m "Automated tag $NEW_TAG"

# Push the new tag to the remote repository
git push origin "$NEW_TAG"

echo "Tag '$NEW_TAG' created and pushed."
