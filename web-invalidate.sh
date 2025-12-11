#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

echo "🔄 MyTower CloudFront Cache Invalidation"
echo "========================================"
echo ""

DISTRIBUTION_NAME="MyTower Web Frontend"

# Get CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Comment=='$DISTRIBUTION_NAME'].Id | [0]" \
    --output text 2>/dev/null)

if [ "$DISTRIBUTION_ID" = "None" ] || [ -z "$DISTRIBUTION_ID" ]; then
    echo "❌ No CloudFront distribution found"
    echo ""
    echo "Run ./deploy-web-to-aws.sh to deploy the frontend first"
    exit 1
fi

echo "Distribution ID: $DISTRIBUTION_ID"
echo ""
echo "Creating invalidation for all files (/*)"
echo ""

if ! INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id "$DISTRIBUTION_ID" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text); then
    echo "❌ Error: Failed to create invalidation"
    exit 1
fi

echo "✅ Invalidation created: $INVALIDATION_ID"
echo ""
echo "This typically takes 1-2 minutes to complete."
echo ""
echo "Check status with:"
echo "  aws cloudfront get-invalidation --distribution-id $DISTRIBUTION_ID --id $INVALIDATION_ID"
echo ""
echo "Or run: ./web-status.sh"
echo ""
