#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

echo "🌐 MyTower Web Frontend Status"
echo "=============================="
echo ""

# Configuration
REGION=us-east-2
BUCKET_NAME=mytower-web-dev
DISTRIBUTION_NAME="MyTower Web Frontend"

# Get CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Comment=='$DISTRIBUTION_NAME'].Id | [0]" \
    --output text 2>/dev/null)

if [ "$DISTRIBUTION_ID" = "None" ] || [ -z "$DISTRIBUTION_ID" ]; then
    echo "❌ No CloudFront distribution found"
    echo ""
    echo "Run ./deploy-web-to-aws.sh to deploy the frontend"
    exit 1
fi

# Get distribution details
echo "☁️  CloudFront Distribution"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

DISTRIBUTION_INFO=$(aws cloudfront get-distribution --id "$DISTRIBUTION_ID" 2>/dev/null)

DOMAIN=$(echo "$DISTRIBUTION_INFO" | grep -oP '"DomainName":\s*"\K[^"]+' | head -1)
STATUS=$(echo "$DISTRIBUTION_INFO" | grep -oP '"Status":\s*"\K[^"]+' | head -1)
ENABLED=$(echo "$DISTRIBUTION_INFO" | grep -oP '"Enabled":\s*\K[^,]+' | head -1)

echo "ID:       $DISTRIBUTION_ID"
echo "Domain:   $DOMAIN"
echo "Status:   $STATUS"
echo "Enabled:  $ENABLED"
echo ""

if [ "$STATUS" = "InProgress" ]; then
    echo "⏳ Distribution is still deploying (this can take 10-15 minutes)"
    echo ""
fi

echo "🌍 Website URL:"
echo "   https://$DOMAIN"
echo ""

# Check S3 bucket
echo "🪣 S3 Bucket Status"
echo "━━━━━━━━━━━━━━━━━━━"

if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "Name:     $BUCKET_NAME"
    echo "Region:   $REGION"

    # Get file count and size with robust error handling
    FILE_COUNT=$(aws s3api list-objects-v2 --bucket "$BUCKET_NAME" --query 'Contents | length(@)' --output text 2>/dev/null)

    # Handle empty bucket or API errors (returns "None" or empty string)
    if [ -z "$FILE_COUNT" ] || [ "$FILE_COUNT" = "None" ]; then
        FILE_COUNT=0
    fi

    BUCKET_SIZE=$(aws s3 ls "s3://$BUCKET_NAME" --recursive --summarize 2>/dev/null | grep "Total Size" | awk '{print $3}')

    # Convert bytes to human readable
    if [ -n "$BUCKET_SIZE" ]; then
        BUCKET_SIZE_MB=$(awk "BEGIN {printf \"%.2f\", $BUCKET_SIZE/1048576}")
        echo "Files:    $FILE_COUNT"
        echo "Size:     ${BUCKET_SIZE_MB} MB"
    fi

    echo ""
    echo "S3 Website URL (direct):"
    echo "   http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"
else
    echo "❌ Bucket not found: $BUCKET_NAME"
fi
echo ""

# Check for recent deployments
echo "📜 Recent Deployments"
echo "━━━━━━━━━━━━━━━━━━━━━"

if [ -d "deployments" ]; then
    RECENT_DEPLOYS=$(ls -t deployments/web-deploy-*.json 2>/dev/null | head -3)

    if [ -n "$RECENT_DEPLOYS" ]; then
        echo "$RECENT_DEPLOYS" | while read -r deploy_file; do
            TIMESTAMP=$(grep -oP '"timestamp":\s*"\K[^"]+' "$deploy_file")
            COMMIT=$(grep -oP '"commit":\s*"\K[^"]+' "$deploy_file")
            echo "• $TIMESTAMP (commit: $COMMIT)"
        done
    else
        echo "No deployment records found"
    fi
else
    echo "No deployments/ directory found"
fi
echo ""

# Check invalidations
echo "🔄 Recent Cache Invalidations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

INVALIDATIONS=$(aws cloudfront list-invalidations \
    --distribution-id "$DISTRIBUTION_ID" \
    --query 'InvalidationList.Items[:3].[Id,Status,CreateTime]' \
    --output text 2>/dev/null)

if [ -n "$INVALIDATIONS" ]; then
    echo "$INVALIDATIONS" | while read -r inv_id inv_status inv_time; do
        echo "• $inv_id - $inv_status ($inv_time)"
    done
else
    echo "No recent invalidations"
fi
echo ""

# AWS Console links
echo "🔗 AWS Console Links"
echo "━━━━━━━━━━━━━━━━━━━━"
echo "CloudFront: https://console.aws.amazon.com/cloudfront/v3/home?region=$REGION#/distributions/$DISTRIBUTION_ID"
echo "S3 Bucket:  https://s3.console.aws.amazon.com/s3/buckets/$BUCKET_NAME?region=$REGION"
echo ""

# Quick commands
echo "💡 Quick Commands"
echo "━━━━━━━━━━━━━━━━━"
echo "Invalidate cache:  ./web-invalidate.sh"
echo "View bucket files: aws s3 ls s3://$BUCKET_NAME --recursive"
echo "Redeploy:          ./deploy-web-to-aws.sh"
echo ""
