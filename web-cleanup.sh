#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

echo "🗑️  MyTower Web Frontend Cleanup"
echo "==============================="
echo ""
echo "⚠️  WARNING: This will DELETE your CloudFront distribution and S3 bucket!"
echo ""

# Configuration
REGION=us-east-2
BUCKET_NAME=mytower-web
DISTRIBUTION_NAME="MyTower Web Frontend"

# Confirm deletion
read -p "Are you sure you want to delete ALL web frontend infrastructure? (type 'yes' to confirm): " -r
echo ""

if [[ ! $REPLY == "yes" ]]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi

# Get CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Comment=='$DISTRIBUTION_NAME'].Id | [0]" \
    --output text 2>/dev/null)

if [ "$DISTRIBUTION_ID" != "None" ] && [ -n "$DISTRIBUTION_ID" ]; then
    echo "☁️  Deleting CloudFront distribution..."

    # Get distribution config
    ETAG=$(aws cloudfront get-distribution-config \
        --id "$DISTRIBUTION_ID" \
        --query 'ETag' \
        --output text)

    # Disable distribution first
    echo "   Disabling distribution..."
    CONFIG=$(aws cloudfront get-distribution-config --id "$DISTRIBUTION_ID" --query 'DistributionConfig' --output json)
    DISABLED_CONFIG=$(echo "$CONFIG" | sed 's/"Enabled": true/"Enabled": false/')

    aws cloudfront update-distribution \
        --id "$DISTRIBUTION_ID" \
        --distribution-config "$DISABLED_CONFIG" \
        --if-match "$ETAG" > /dev/null 2>&1

    echo "   ⏳ Waiting for distribution to be disabled (this takes ~5 minutes)..."
    echo "   You can check status with: ./web-status.sh"
    echo ""
    echo "   Once disabled, run this command to complete deletion:"
    echo "   aws cloudfront delete-distribution --id $DISTRIBUTION_ID --if-match <NEW_ETAG>"
    echo ""
    echo "   To get the new ETAG:"
    echo "   aws cloudfront get-distribution-config --id $DISTRIBUTION_ID --query 'ETag' --output text"
    echo ""
else
    echo "✅ No CloudFront distribution found to delete"
fi

# Delete S3 bucket
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "🪣 Deleting S3 bucket..."

    # Empty bucket first
    echo "   Emptying bucket..."
    aws s3 rm "s3://$BUCKET_NAME" --recursive

    # Delete bucket
    echo "   Deleting bucket..."
    aws s3api delete-bucket --bucket "$BUCKET_NAME" --region "$REGION"

    if [ $? -eq 0 ]; then
        echo "   ✅ Bucket deleted: $BUCKET_NAME"
    else
        echo "   ❌ Error deleting bucket"
    fi
else
    echo "✅ No S3 bucket found to delete"
fi

echo ""
echo "🧹 Cleanup complete!"
echo ""
echo "Note: CloudFront distribution deletion is a two-step process:"
echo "  1. Disable the distribution (done above)"
echo "  2. Wait ~5 minutes for it to deploy"
echo "  3. Delete the distribution with the new ETag"
echo ""
