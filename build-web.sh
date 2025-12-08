#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

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
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: npm install failed"
        exit 1
    fi
    echo "   ✅ Dependencies installed"
    echo ""
fi

# Run type checking
echo "🔍 Running type checks..."
npm run check
if [ $? -ne 0 ]; then
    echo "❌ Error: Type check failed"
    echo "   Fix TypeScript errors before deploying"
    exit 1
fi
echo "   ✅ Type checks passed"
echo ""

# Build production bundle
echo "🏗️  Building production bundle..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Error: Build failed"
    exit 1
fi
echo "   ✅ Build completed"
echo ""

# Show build output
if [ -d "dist" ]; then
    echo "📊 Build Output:"
    du -sh dist
    echo ""
    echo "📁 Files in dist/:"
    ls -lh dist/
    echo ""
    echo "✅ Build successful! Ready to deploy."
else
    echo "❌ Error: dist/ directory not found after build"
    exit 1
fi
