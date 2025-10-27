#!/bin/bash

echo "🚀 MyTower AWS Deployment Script"
echo "================================"
echo ""

# Configuration
REGION=us-east-2
REPOSITORY_NAME=mytower-server

# Get account ID
echo "📋 Getting AWS account info..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Error: Unable to get AWS account ID. Are you logged in?"
    exit 1
fi

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
IMAGE_URI="${ECR_URI}/${REPOSITORY_NAME}:latest"

echo "   ✅ Account: $ACCOUNT_ID"
echo "   ✅ Region: $REGION"
echo "   ✅ Image: $IMAGE_URI"
echo ""

# Check if there are uncommitted changes
echo "�� Checking git status..."
if [[ -n $(git status -s) ]]; then
    echo "⚠️  Warning: You have uncommitted changes!"
    git status -s
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

BRANCH=$(git branch --show-current)
COMMIT=$(git rev-parse --short HEAD)
echo "   ✅ Branch: $BRANCH"
echo "   ✅ Commit: $COMMIT"
echo ""

# Build Docker image
echo "🔨 Building Docker image for AMD64..."
docker build --platform linux/amd64 -t ${REPOSITORY_NAME}:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "   ✅ Build complete"
echo ""

# Tag image
echo "🏷️  Tagging image..."
docker tag ${REPOSITORY_NAME}:latest $IMAGE_URI
echo "   ✅ Tagged: $IMAGE_URI"
echo ""

# Login to ECR
echo "🔐 Authenticating with ECR..."
aws ecr get-login-password --region $REGION | \
    docker login --username AWS --password-stdin $ECR_URI

if [ $? -ne 0 ]; then
    echo "❌ ECR authentication failed!"
    exit 1
fi

echo "   ✅ Authenticated"
echo ""

# Push to ECR
echo "📤 Pushing image to ECR (this may take a few minutes)..."
docker push $IMAGE_URI

if [ $? -ne 0 ]; then
    echo "❌ Push to ECR failed!"
    exit 1
fi

echo "   ✅ Image pushed successfully"
echo ""

# Check if there are running tasks
echo "🔍 Checking for running tasks..."
RUNNING_TASKS=$(aws ecs list-tasks \
    --cluster mytower-cluster \
    --desired-status RUNNING \
    --region $REGION \
    --query 'taskArns' \
    --output text)

if [ -n "$RUNNING_TASKS" ] && [ "$RUNNING_TASKS" != "None" ]; then
    echo "   ⚠️  Found running task(s)"
    echo ""
    read -p "Stop existing task and start new one? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Stopping existing task(s)..."
        for TASK in $RUNNING_TASKS; do
            aws ecs stop-task \
                --cluster mytower-cluster \
                --task $TASK \
                --region $REGION \
                --query 'task.taskArn' \
                --output text
        done
        echo "   ✅ Stopped"
        echo ""

        # Wait a moment for tasks to stop
        echo "⏳ Waiting for tasks to stop..."
        sleep 5
        echo ""
    else
        echo "ℹ️  Existing tasks will continue running with old image"
        echo "   Run ./run-task.sh manually to start a task with new image"
        echo ""
        echo "✅ Deployment complete!"
        exit 0
    fi
fi

# Start new task
echo "🎮 Starting new task with updated image..."
./run-task.sh

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Deployment Summary:"
echo "   Branch: $BRANCH"
echo "   Commit: $COMMIT"
echo "   Image: $IMAGE_URI"
echo "   Region: $REGION"

# After successful deployment, add this before the summary:
echo "🏷️  Creating git tag..."
TAG="deploy-$(date +%Y%m%d-%H%M%S)"
git tag -a $TAG -m "Deployed to AWS: $COMMIT"
echo "   ✅ Tagged: $TAG"
echo "   Push tag with: git push origin $TAG"s
