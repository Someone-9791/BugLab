#!/bin/bash
# Deploy to HuggingFace Spaces with HF-specific README
# This script manages separate READMEs for GitHub and HF Spaces

set -e

echo "🚀 Deploying to HuggingFace Spaces..."

# Store the current git configuration
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Ensure we're on main branch
git checkout main

# Create a temporary commit with README_HF.md as README.md
echo "📝 Preparing HF Spaces version..."
cp README_HF.md README.md

# Commit the HF version
git add README.md
git commit -m "chore: Deploy with HF Spaces metadata [skip ci]" || true

# Push to HF Spaces remote
echo "⬆️  Pushing to HuggingFace Spaces..."
git push hf main --force

# Restore the clean GitHub README
echo "🔄 Restoring GitHub version..."
git checkout HEAD~1 -- README.md 2>/dev/null || git checkout HEAD -- README.md
git add README.md
git commit -m "chore: Restore clean README for GitHub [skip ci]" || true

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push origin main

echo "✅ Deployment complete!"
echo "   ✓ GitHub: Clean README (no YAML)"
echo "   ✓ HF Spaces: README with metadata"
