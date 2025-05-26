#!/bin/bash

# Project Cleanup Script
# Run this script to remove unnecessary files and reduce project size

echo "🧹 Starting project cleanup..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
find . -name "*.pyd" -type f -delete 2>/dev/null || true

# Remove macOS system files
echo "Removing macOS system files..."
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true

# Remove temporary files
echo "Removing temporary files..."
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.temp" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true

# Remove log files (optional - uncomment if needed)
# echo "Removing log files..."
# find . -name "*.log" -type f -delete 2>/dev/null || true

echo "✅ Cleanup complete!"
echo "📊 Current project size:"
du -sh . 