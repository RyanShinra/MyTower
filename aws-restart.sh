#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

echo "[REFRESH] Restarting MyTower ECS Task..."
echo ""

REGION=us-east-2

# Get running task ARN
TASK_ARN=$(aws ecs list-tasks \
    --cluster mytower-cluster \
    --desired-status RUNNING \
    --region $REGION \
    --query 'taskArns[0]' \
    --output text)

if [ "$TASK_ARN" != "None" ] && [ -n "$TASK_ARN" ]; then
    echo "[STOP] Stopping current task: $TASK_ARN"
    aws ecs stop-task \
        --cluster mytower-cluster \
        --task $TASK_ARN \
        --region $REGION \
        --query 'task.taskArn' \
        --output text
    
    echo "[WAIT] Waiting for task to stop..."
    sleep 10
fi

echo ""
echo "[START] Starting new task..."

# Run the existing start script
./aws-run.sh
