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

# Clean up any existing content
rm -rf /src/*

# Clone the repository
echo "Cloning repository..."
git clone --depth 1 --branch "$GIT_BRANCH" "$GIT_REPO" /src

# Check if this is a Hugo site
if [ ! -f "/src/config.yaml" ] && [ ! -f "/src/config.toml" ] && [ ! -f "/src/config.yml" ] && [ ! -f "/src/hugo.yaml" ] && [ ! -f "/src/hugo.toml" ] && [ ! -f "/src/hugo.yml" ]; then
    echo "No Hugo configuration found. Creating basic Hugo site..."
    
    # Create basic Hugo structure (only if directories don't exist)
    mkdir -p layouts/_default static
    
    # Create basic config
    cat > config.yaml << EOF
baseURL: 'http://localhost'
languageCode: 'en-us'
title: 'ModernWiki'

markup:
  goldmark:
    renderer:
      unsafe: true
  
params:
  description: 'A modern Wiki powered by Hugo'
EOF

    # Create basic layout
    cat > layouts/_default/baseof.html << 'EOF'
<!DOCTYPE html>
<html lang="{{ .Site.LanguageCode }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ .Title }} - {{ .Site.Title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        h1, h2, h3 { color: #333; }
        nav { background: #f4f4f4; padding: 10px 0; margin-bottom: 20px; }
        nav ul { list-style: none; padding: 0; margin: 0; }
        nav li { display: inline-block; margin-right: 20px; }
        nav a { text-decoration: none; color: #333; }
        nav a:hover { color: #007acc; }
        .content { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <ul>
                <li><a href="/">Home</a></li>
            </ul>
        </div>
    </nav>
    <div class="container">
        <div class="content">
            {{ block "main" . }}{{ end }}
        </div>
    </div>
</body>
</html>
EOF

    # Create basic single page layout
    cat > layouts/_default/single.html << 'EOF'
{{ define "main" }}
<h1>{{ .Title }}</h1>
<div>{{ .Content }}</div>
{{ end }}
EOF

    # Create basic list layout
    cat > layouts/_default/list.html << 'EOF'
{{ define "main" }}
<h1>{{ .Title }}</h1>
{{ if .Content }}
<div>{{ .Content }}</div>
{{ end }}
{{ range .Pages }}
<h2><a href="{{ .Permalink }}">{{ .Title }}</a></h2>
<p>{{ .Summary }}</p>
{{ end }}
{{ end }}
EOF

    # Create home page content if not exists
    if [ ! -f "content/_index.md" ]; then
        mkdir -p content
        cat > content/_index.md << 'EOF'
---
title: "Welcome to ModernWiki"
---

# Welcome to ModernWiki

This is a modern Wiki powered by Hugo and Git. 

## Features

- Git-based content management
- Static site generation with Hugo
- Automatic rebuilding via webhooks
- Clean, responsive design

## Getting Started

Create Markdown files in the `content/` directory to add new pages to your wiki.
EOF
    fi
fi

# Build the site
echo "Building Hugo site..."
hugo --destination "$SITE_DIR" --cleanDestinationDir

echo "Hugo site build completed successfully!"
echo "Site generated in: $SITE_DIR"

# List generated files for debugging
echo "Generated files:"
find "$SITE_DIR" -type f | head -10