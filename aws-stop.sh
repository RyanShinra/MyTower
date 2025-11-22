#!/bin/bash

# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

echo "🛑 Stopping MyTower ECS Task..."
echo ""

REGION=us-east-2

# Get running task ARN
TASK_ARN=$(aws ecs list-tasks \
    --cluster mytower-cluster \
    --desired-status RUNNING \
    --region $REGION \
    --query 'taskArns[0]' \
    --output text)

if [ "$TASK_ARN" == "None" ] || [ -z "$TASK_ARN" ]; then
    echo "ℹ️  No running tasks found"
    exit 0
fi

echo "🎯 Found task: $TASK_ARN"
echo "   Stopping..."

aws ecs stop-task \
    --cluster mytower-cluster \
    --task $TASK_ARN \
    --region $REGION

echo ""
echo "✅ Task stopped!"
