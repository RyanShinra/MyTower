# Requirements Files Migration Guide

## Overview

Your requirements have been split into three files for better organization:

### 1. `requirements-base.txt` (NEW)
**Core runtime dependencies** - Used by both headless and desktop modes
- strawberry-graphql
- uvicorn
- fastapi
- typing_extensions

### 2. `requirements-server.txt` (NEW)
**AWS/Production only** - Minimal dependencies for deployment
- Includes: requirements-base.txt
- Adds: Production-optimized uvicorn
- Excludes: pygame, all dev tools

### 3. `requirements-dev.txt` (NEW)
**Full development environment** - Everything you need locally
- Includes: requirements-base.txt
- Adds: pygame, pytest, black, mypy, etc.
- This replaces your old `requirements.txt`

---

## Migration Steps

### 1. Backup your current requirements.txt
```bash
cp requirements.txt requirements.txt.backup
```

### 2. Copy the new split files to your project root
```bash
# Copy these three files to your project directory:
# - requirements-base.txt
# - requirements-server.txt
# - requirements-dev.txt
```

### 3. Update your virtual environment (local development)
```bash
# Deactivate current venv
deactivate

# Remove old venv
rm -rf .venv

# Create fresh venv
python3.13 -m venv .venv
source .venv/bin/activate

# Install dev dependencies (includes everything)
pip install -r requirements-dev.txt
```

### 4. Keep old requirements.txt (optional)
You can keep `requirements.txt` as-is for backward compatibility, but:
- Use `requirements-dev.txt` for local development
- Use `requirements-headless.txt` for Docker/AWS

---

## Usage by Environment

### Local Development (Desktop + Tests)
```bash
pip install -r requirements-dev.txt
```

### AWS/Production (Server Mode)
```bash
pip install -r requirements-server.txt
```

### Docker Build
The Dockerfile now uses `requirements-server.txt` automatically.

---

## Benefits of This Split

✅ **Smaller Docker images** - No pygame or dev tools in production
✅ **Faster deployments** - Fewer dependencies to install
✅ **Clearer separation** - Know what's needed where
✅ **Cost savings** - Smaller images = less storage/bandwidth on AWS

---

## Verification

After installing, verify you have the right packages:

### For Development:
```bash
python -c "import pygame; import pytest; print('Dev environment OK')"
```

### For Server Mode:
```bash
python -c "import fastapi; import strawberry; print('Server environment OK')"
# This should work:
python -m mytower.main --mode headless --port 8000
```

---

## Troubleshooting

### "Module not found" errors in dev
```bash
# You probably installed server by mistake
pip install -r requirements-dev.txt
```

### Docker build fails
```bash
# Make sure both files are in project root
ls requirements-base.txt requirements-server.txt
```

### Want to go back to single file
Just use your `requirements.txt.backup`:
```bash
cp requirements.txt.backup requirements.txt
pip install -r requirements.txt
```
