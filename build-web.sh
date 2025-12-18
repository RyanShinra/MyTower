#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

echo "[BUILD] MyTower Web Frontend Build Script"
echo "=========================================="
echo ""

# Navigate to web directory
cd web || {
    echo "[ERROR] web/ directory not found"
    exit 1
}

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "[INSTALL] Installing dependencies..."

    if ! npm install; then
        echo "[ERROR] npm install failed"
        exit 1
    fi
    echo "   [OK] Dependencies installed"
    echo ""
fi

# Run type checking
echo "[CHECK] Running type checks..."
if ! npm run check; then
    echo "[ERROR] Type check failed"
    echo "   Fix TypeScript errors before deploying"
    exit 1
fi
echo "   [OK] Type checks passed"
echo ""

# Build production bundle
echo "[BUILD] Building production bundle..."
if ! npm run build; then
    echo "[ERROR] Build failed"
    exit 1
fi
echo "   [OK] Build completed"
echo ""

# Show build output
if [ -d "dist" ]; then
    echo "[INFO] Build Output:"
    if du -sh dist 2>/dev/null; then
        true # it's already printed human-readable size
    elif du -s dist 2>/dev/null; then
        SIZE=$(du -s dist | awk '{print $1}')
        echo "Size: $SIZE KB"
    else
        echo "Size calculation unavailable (du not supported)"
    fi
    echo ""
    echo "[INFO] Files in dist/:"
    ls -lh dist/
    echo ""
    echo "[SUCCESS] Build successful! Ready to deploy."
else
    echo "[ERROR] dist/ directory not found after build"
    exit 1
fi
