#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.


echo "[DOCKER] Running MyTower Docker Container Locally"
echo "==========================================="
echo ""

# Configuration
CONTAINER_NAME=mytower-local
IMAGE_NAME=mytower-server
PORT=8000

# Check if container is already running
echo "[CHECK] Checking for existing container..."
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "   [WARNING]  Container '$CONTAINER_NAME' is already running"
    read -p "Stop and restart? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "[STOP] Stopping existing container..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        echo "   [OK] Stopped"
    else
        echo "[INFO] Keeping existing container running"
        echo "   Access at: http://localhost:$PORT/graphql"
        exit 0
    fi
fi

# Clean up stopped container if it exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "[CLEAN] Removing old container..."
    docker rm $CONTAINER_NAME
fi

# Build the image
echo ""
echo "[BUILD] Building Docker image..."
if ! docker build -t $IMAGE_NAME .; then
    echo "[ERROR] Docker build failed!"
    exit 1
fi

echo "   [OK] Build complete"
echo ""

# Run the container
echo "[START] Starting container..."
if ! docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    -e MYTOWER_MODE=headless \
    -e MYTOWER_PORT=$PORT \
    -e MYTOWER_LOG_LEVEL=INFO \
    $IMAGE_NAME; then
    echo "[ERROR] Failed to start container!"
    exit 1
fi

echo "   [OK] Container started: $CONTAINER_NAME"
echo ""

# Wait a moment for the server to start
echo "[WAIT] Waiting for server to start..."
sleep 3

# Check if it's responding
echo "[CHECK] Checking server health..."
if curl -s http://localhost:$PORT/ > /dev/null; then
    echo "   [OK] Server is responding!"
else
    echo "   [WARNING]  Server might not be ready yet"
fi

echo ""
echo "[OK] Container is running!"
echo ""
echo "[WEB] Access points:"
echo "   GraphQL Playground: http://localhost:$PORT/graphql"
echo "   Health check:       http://localhost:$PORT/"
echo ""
echo "[INFO] View logs with:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "[STOP] Stop container with:"
echo "   docker stop $CONTAINER_NAME"
echo ""
echo "[DEBUG] Debug inside container:"
echo "   docker exec -it $CONTAINER_NAME /bin/bash"
