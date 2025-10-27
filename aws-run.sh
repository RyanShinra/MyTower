#!/bin/bash

echo "🚀 Starting MyTower ECS Task..."
echo ""

# Load environment variables
echo "📋 Loading AWS environment..."
export REGION=us-east-2
export VPC_ID=$(aws ec2 describe-vpcs --region $REGION --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
export SUBNET_ID=$(aws ec2 describe-subnets --region $REGION --filters "Name=vpc-id,Values=${VPC_ID}" --query "Subnets[0].SubnetId" --output text)
export SG_ID=$(aws ec2 describe-security-groups --region $REGION --filters "Name=group-name,Values=mytower-sg" --query "SecurityGroups[0].GroupId" --output text)
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "   ✅ VPC: $VPC_ID"
echo "   ✅ Subnet: $SUBNET_ID"
echo "   ✅ Security Group: $SG_ID"
echo ""

# Run the task
echo "🎮 Starting ECS task..."
TASK_ARN=$(aws ecs run-task \
    --cluster mytower-cluster \
    --task-definition mytower-task \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_ID}],securityGroups=[${SG_ID}],assignPublicIp=ENABLED}" \
    --region $REGION \
    --query 'tasks[0].taskArn' \
    --output text)

echo "   ✅ Task ARN: $TASK_ARN"
echo ""
echo "⏳ Waiting for task to start (this takes ~30-60 seconds)..."

# Wait for task to be running
aws ecs wait tasks-running \
    --cluster mytower-cluster \
    --tasks $TASK_ARN \
    --region $REGION

# Get the network interface ID
ENI_ID=$(aws ecs describe-tasks \
    --cluster mytower-cluster \
    --tasks $TASK_ARN \
    --region $REGION \
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
    --output text)

# Get the public IP from the network interface
PUBLIC_IP=$(aws ec2 describe-network-interfaces \
    --network-interface-ids $ENI_ID \
    --region $REGION \
    --query 'NetworkInterfaces[0].Association.PublicIp' \
    --output text)

echo ""
echo "✅ Task is running!"
echo ""
echo "🌐 Public IP: $PUBLIC_IP"
echo "🔗 GraphQL Playground: http://$PUBLIC_IP:8000/graphql"
echo ""
echo "📊 View logs with:"
echo "   aws logs tail /ecs/mytower-server --follow --region $REGION"
echo ""
echo "🛑 Stop task with:"
echo "   ./stop-task.sh"
