#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.


echo "[INFO] MyTower ECS Status"
echo ""

REGION=us-east-2

# List running tasks
echo "[OK] Running tasks:"
aws ecs list-tasks \
    --cluster mytower-cluster \
    --desired-status RUNNING \
    --region $REGION

echo ""
echo "[STOPPED] Stopped tasks (recent):"
aws ecs list-tasks \
    --cluster mytower-cluster \
    --desired-status STOPPED \
    --region $REGION

echo ""
echo "[LOG] To get task details (including public IP):"
echo "   Go to: https://us-east-2.console.aws.amazon.com/ecs/v2/clusters/mytower-cluster/tasks"
