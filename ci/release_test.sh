#!/bin/bash
set -e

echo "Current branch: $(git branch --show-current)"

VERSION=$(uv version --short)
echo "Current version: $VERSION"

echo "Dry-run: uv version --bump ${VERSION_TYPE:-patch}"
uv version --dry-run --bump ${VERSION_TYPE:-patch}

NEW_VERSION=$(uv version --short)
echo "Would commit version bump for $NEW_VERSION"
echo "Would push commit to main: git push origin main"
echo "Would create tag: git tag v$NEW_VERSION"
echo "Would push tag: git push origin v$NEW_VERSION"