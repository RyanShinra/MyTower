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

# Warn if in detached HEAD state
if [ -z "$BRANCH" ]; then
    echo "   ⚠️  Warning: Git is in detached HEAD state"
    BRANCH="detached-HEAD"
fi

echo "   ✅ Branch: $BRANCH"
echo "   ✅ Commit: $COMMIT"
echo ""

# Build Docker image
echo "🔨 Building Docker image for AMD64..."
docker build --platform linux/amd64 -t "${REPOSITORY_NAME}:latest" .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "   ✅ Build complete"
echo ""

# Tag image
echo "🏷️  Tagging image..."
docker tag "${REPOSITORY_NAME}:latest" "$IMAGE_URI"
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
docker push "$IMAGE_URI"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to push image to ECR!"
    echo "   This could be due to:"
    echo "   - Network connectivity issues"
    echo "   - ECR repository does not exist"
    echo "   - Insufficient permissions"
    exit 1
fi

echo "   ✅ Image pushed successfully"
echo ""

# Verify push by pulling image
echo "🔍 Verifying image push (pulling from ECR)..."
docker pull "$IMAGE_URI"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull image from ECR!"
    echo "   The image was pushed but cannot be pulled back."
    echo "   This indicates the push may have been incomplete or corrupted."
    echo "   Please retry the deployment."
    exit 1
fi

echo "   ✅ Image verified - pull successful"
echo ""

# Create deployment metadata
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DEPLOY_TAG="deploy-$(date -u +%Y%m%d-%H%M%S)"
METADATA_FILE="deployments/${DEPLOY_TAG}.json"

echo "📝 Creating deployment metadata..."
mkdir -p deployments

if [ $? -ne 0 ]; then
    echo "   ⚠️  Warning: Failed to create deployments directory"
else
    cat > "$METADATA_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "deploy_tag": "$DEPLOY_TAG",
  "branch": "$BRANCH",
  "commit": "$COMMIT",
  "commit_full": "$(git rev-parse HEAD)",
  "image_uri": "$IMAGE_URI",
  "region": "$REGION",
  "repository": "$REPOSITORY_NAME"
}
EOF

    if [ -f "$METADATA_FILE" ]; then
        echo "   ✅ Metadata saved to: $METADATA_FILE"
    else
        echo "   ⚠️  Warning: Failed to create metadata file"
    fi
fi
echo ""

# Create git tag for successful deployment
echo "🏷️  Creating git tag..."
git tag -a "$DEPLOY_TAG" -m "Deployed to AWS: $COMMIT on $TIMESTAMP"

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to create git tag (deployment was successful)"
else
    echo "   ✅ Tagged: $DEPLOY_TAG"

    # Automatically push the tag
    echo "📤 Pushing tag to remote..."
    git push origin "$DEPLOY_TAG"

    if [ $? -ne 0 ]; then
        echo "   ⚠️  Warning: Failed to push tag (tag created locally)"
        echo "   💡 Push manually with: git push origin $DEPLOY_TAG"
    else
        echo "   ✅ Tag pushed to remote"
    fi
fi
echo ""
# Check if there are running tasks
echo "🔍 Checking for running tasks..."
RUNNING_TASKS=$(aws ecs list-tasks \
    --cluster mytower-cluster \
    --desired-status RUNNING \
    --region $REGION \
    --query 'taskArns' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    echo "   ⚠️  Warning: Failed to check ECS tasks (cluster may not exist)"
    echo "   Deployment successful! Manually start tasks if needed."
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📝 Deployment Summary:"
    echo "   Branch: $BRANCH"
    echo "   Commit: $COMMIT"
    echo "   Image: $IMAGE_URI"
    echo "   Region: $REGION"
    echo "   Deploy Tag: $DEPLOY_TAG"
    echo "   Metadata: $METADATA_FILE"
    exit 0
fi

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

# Check if run-task.sh exists and is executable
if [ ! -f "./run-task.sh" ]; then
    echo "   ⚠️  Warning: run-task.sh not found"
    echo "   Deployment successful, but cannot start new task automatically"
    echo "   Create and run run-task.sh manually to start the task"
elif [ ! -x "./run-task.sh" ]; then
    echo "   ⚠️  Warning: run-task.sh is not executable"
    echo "   Run: chmod +x run-task.sh"
else
    ./run-task.sh
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Deployment Summary:"
echo "   Branch: $BRANCH"
echo "   Commit: $COMMIT"
echo "   Image: $IMAGE_URI"
echo "   Region: $REGION"
echo "   Deploy Tag: $DEPLOY_TAG"
echo "   Metadata: $METADATA_FILE"
