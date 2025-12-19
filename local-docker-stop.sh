#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.


CONTAINER_NAME=mytower-local

echo "🛑 Stopping MyTower Docker Container"
echo ""

if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "[INFO] Container '$CONTAINER_NAME' is not running"
    exit 0
fi

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo "   ✅ Container stopped and removed"
