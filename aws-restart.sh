#!/bin/bash

echo "Ì¥Ñ Restarting MyTower ECS Task..."
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
    echo "Ìªë Stopping current task: $TASK_ARN"
    aws ecs stop-task \
        --cluster mytower-cluster \
        --task $TASK_ARN \
        --region $REGION \
        --query 'task.taskArn' \
        --output text
    
    echo "‚è≥ Waiting for task to stop..."
    sleep 10
fi

echo ""
echo "ÌæÆ Starting new task..."

# Run the existing start script
./aws-run.sh
