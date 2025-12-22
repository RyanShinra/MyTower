#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.


CONTAINER_NAME=mytower-local

echo "[INFO] Tailing logs from $CONTAINER_NAME..."
echo "Press Ctrl+C to exit"
echo ""

docker logs -f $CONTAINER_NAME
