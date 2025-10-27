#!/bin/bash

CONTAINER_NAME=mytower-local

echo "📊 Tailing logs from $CONTAINER_NAME..."
echo "Press Ctrl+C to exit"
echo ""

docker logs -f $CONTAINER_NAME
