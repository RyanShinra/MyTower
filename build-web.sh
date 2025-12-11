#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

echo "🎨 MyTower Web Frontend Build Script"
echo "===================================="
echo ""

# Navigate to web directory
cd web || {
    echo "❌ Error: web/ directory not found"
    exit 1
}

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    
    if ! npm install; then
        echo "❌ Error: npm install failed"
        exit 1
    fi
    echo "   ✅ Dependencies installed"
    echo ""
fi

# Run type checking
echo "🔍 Running type checks..."
if ! npm run check; then
    echo "❌ Error: Type check failed"
    echo "   Fix TypeScript errors before deploying"
    exit 1
fi
echo "   ✅ Type checks passed"
echo ""

# Build production bundle
echo "🏗️  Building production bundle..."
if ! npm run build; then
    echo "❌ Error: Build failed"
    exit 1
fi
echo "   ✅ Build completed"
echo ""

# Show build output
if [ -d "dist" ]; then
    echo "📊 Build Output:"
    if du -sh dist 2>/dev/null; then
        : # already printed human-readable size
    elif du -s dist 2>/dev/null; then
        SIZE=$(du -s dist | awk '{print $1}')
        echo "Size: $SIZE KB"
    else
        echo "Size calculation unavailable (du not supported)"
    fi
    echo ""
    echo "📁 Files in dist/:"
    ls -lh dist/
    echo ""
    echo "✅ Build successful! Ready to deploy."
else
    echo "❌ Error: dist/ directory not found after build"
    exit 1
fi
