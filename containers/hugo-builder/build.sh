#!/bin/sh

# Environment variables:
# GIT_REPO - Git repository URL
# GIT_BRANCH - Git branch (default: main)
# SITE_DIR - Output directory for static site (default: /site)

set -e

GIT_BRANCH=${GIT_BRANCH:-main}
SITE_DIR=${SITE_DIR:-/site}

echo "Starting Hugo site build..."
echo "Git repo: ${GIT_REPO}"
echo "Git branch: ${GIT_BRANCH}"
echo "Output directory: ${SITE_DIR}"

if [ -z "$GIT_REPO" ]; then
    echo "Error: GIT_REPO environment variable is required"
    exit 1
fi

# Clean up any existing content，include .git folder
rm -rf /src/*
rm -rf /src/.* 2> /dev/null
find "/src/" -type f | head -20

# Clone the repository
echo "Cloning repository..."
git clone --depth 1 --branch "$GIT_BRANCH" "$GIT_REPO" /src
cd /src
git submodule update --init --recursive

# Check if this is a Hugo site
if [ ! -f "/src/config.yaml" ] && [ ! -f "/src/config.toml" ] && [ ! -f "/src/config.yml" ] && [ ! -f "/src/hugo.yaml" ] && [ ! -f "/src/hugo.toml" ] && [ ! -f "/src/hugo.yml" ]; then
    echo "No Hugo configuration found. Creating basic Hugo site..."
    
    rm -rf /src/*
    git clone --depth 1 --branch "master" "https://github.com/Heerozh/ModernWikiTemplate.git" /src

fi

# Save the Git remote URL to a file for reference
GIT_REMOTE_URL=$(git config --get remote.origin.url)
CURRENT_BRANCH=$(git branch --show-current)
mkdir -p data
cat > data/gitremote.toml << EOF
url = "$GIT_REMOTE_URL"
branch = "$CURRENT_BRANCH"
EOF

# Build the site
echo "Building Hugo site..."
echo "Source files:"
find "./content/" -type f | head -20
hugo --destination "$SITE_DIR" --cleanDestinationDir

echo "Hugo site build completed successfully!"
echo "Site generated in: $SITE_DIR"

# List generated files for debugging
echo "Generated files:"
find "$SITE_DIR" -type f | head -20