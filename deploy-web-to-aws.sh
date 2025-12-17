#!/bin/bash
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

echo "🌐 MyTower Web Frontend Deployment to AWS"
echo "=========================================="
echo ""

# Configuration
REGION=us-east-2
BUCKET_NAME=mytower-web-dev
DISTRIBUTION_NAME="MyTower Web Frontend"

# Get account ID
echo "📋 Getting AWS account info..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)

if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Error: Unable to get AWS account ID. Are you logged in?"
    echo ""
    echo "Run: aws configure"
    echo "Or check your credentials with: aws sts get-caller-identity"
    exit 1
fi

echo "   ✅ Account: $ACCOUNT_ID"
echo "   ✅ Region: $REGION"
echo ""

# Check if dist/ exists
if [ ! -d "web/dist" ]; then
    echo "❌ Error: web/dist/ directory not found"
    echo ""
    echo "Run ./build-web.sh first to build the frontend"
    exit 1
fi

# Step 1: Create S3 bucket (if it doesn't exist)
echo "🪣 Setting up S3 bucket..."
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "   ✅ Bucket already exists: $BUCKET_NAME"
else
    echo "   Creating bucket: $BUCKET_NAME"

    # Create bucket (us-east-1 doesn't need LocationConstraint, others do)
    # With set -e, the script exits automatically on failure, but we wrap in if !
    # to provide a helpful error message
    if [ "$REGION" = "us-east-1" ]; then
        if ! aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION"; then
            echo "❌ Error: Failed to create S3 bucket"
            echo ""
            echo "Common issues:"
            echo "  - Bucket name already taken globally"
            echo "  - Insufficient permissions"
            echo ""
            echo "Try adding your AWS account ID to the bucket name:"
            echo "  BUCKET_NAME=mytower-web-dev-$ACCOUNT_ID"
            exit 1
        fi
    else
        if ! aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION"; then
            echo "❌ Error: Failed to create S3 bucket"
            echo ""
            echo "Common issues:"
            echo "  - Bucket name already taken globally"
            echo "  - Insufficient permissions"
            echo ""
            echo "Try adding your AWS account ID to the bucket name:"
            echo "  BUCKET_NAME=mytower-web-dev-$ACCOUNT_ID"
            exit 1
        fi
    fi

    echo "   ✅ Bucket created"
fi
echo ""

# Step 2: Enable static website hosting
echo "🌍 Configuring static website hosting..."
if ! aws s3 website "s3://$BUCKET_NAME" \
    --index-document index.html \
    --error-document index.html; then
    echo "❌ Error: Failed to configure static website hosting"
    exit 1
fi
echo "   ✅ Static website hosting enabled"
echo ""

# Step 3: Set bucket policy for public read access
echo "🔓 Setting bucket policy for public access..."
echo ""
echo "⚠️  SECURITY NOTE: This will make all files in the bucket publicly readable."
echo "   This is required for static website hosting."
echo "   Only deploy public website content to this bucket."
echo ""
read -p "Continue with public bucket configuration? (y/N): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled - bucket policy not configured"
    echo "   Note: The bucket was created but is not publicly accessible"
    exit 1
fi

# First, disable block public access settings
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Create bucket policy JSON
# SECURITY: This policy allows public read access to all objects (Principal: "*")
# This is intentional for static website hosting, but means ALL files in this
# bucket will be publicly accessible. Never store sensitive data in this bucket.
POLICY=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF
)

if ! aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy "$POLICY"; then
    echo "❌ Error: Failed to set bucket policy"
    exit 1
fi
echo "   ✅ Bucket policy configured for public read access"
echo ""

# Step 4: Upload files to S3
echo "📤 Uploading files to S3..."
# Upload strategy: Assets FIRST, then HTML/JSON
# Why? With fingerprinted assets (e.g., main-abc123.js), the correct order is:
#   1. Upload new assets → Safe, old HTML doesn't reference them yet
#   2. Upload new HTML → Now references assets that already exist
# If we upload HTML first and assets fail, users get HTML referencing
# non-existent assets (broken site). If we upload assets first and HTML fails,
# users continue seeing old HTML with old (still existing) assets (site still works).

# Upload static assets with 1-year cache (safe due to fingerprinted filenames)
echo "   Uploading static assets (1-year cache)..."
if ! aws s3 sync web/dist/ "s3://$BUCKET_NAME" \
    --delete \
    --cache-control "max-age=31536000,public" \
    --exclude "*.html" \
    --exclude "*.json"; then
    echo "❌ Error: Failed to upload static assets to S3"
    exit 1
fi

# Upload HTML and JSON with no cache (always fresh)
# Upload these LAST so they only go live once assets are confirmed uploaded
echo "   Uploading HTML and JSON files (no-cache)..."
if ! aws s3 sync web/dist/ "s3://$BUCKET_NAME" \
    --cache-control "max-age=0,no-cache,no-store,must-revalidate" \
    --exclude "*" \
    --include "*.html" \
    --include "*.json"; then
    echo "❌ Error: Failed to upload HTML/JSON files to S3"
    exit 1
fi

echo "   ✅ All files uploaded successfully"
echo ""

# Step 5: Get or create CloudFront distribution
echo "☁️  Setting up CloudFront distribution..."

# Check if distribution already exists
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Comment=='$DISTRIBUTION_NAME'].Id | [0]" \
    --output text)

if [ "$DISTRIBUTION_ID" = "None" ] || [ -z "$DISTRIBUTION_ID" ]; then
    echo "   Creating new CloudFront distribution..."
    echo "   ⚠️  This takes 10-15 minutes to fully deploy"
    echo ""

    # Get S3 website endpoint
    # Note: Format is different for us-east-1 vs other regions
    # us-east-1: bucket-name.s3-website-us-east-1.amazonaws.com
    # Other regions: bucket-name.s3-website-REGION.amazonaws.com (hyphen, not dot)
    WEBSITE_ENDPOINT="${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"

    # Create distribution config
    # TODO: Extract CloudFront distribution config to a separate JSON template file for easier maintenance and validation.
    # NOTE: If cross-origin requests to S3 are needed in the future, add OriginRequestPolicyId to DefaultCacheBehavior:
    #       "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf"  (CORS-S3Origin managed policy)
    DIST_CONFIG=$(cat <<EOF
{
    "CallerReference": "mytower-web-dev-$(date +%s)",
    "Comment": "$DISTRIBUTION_NAME",
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$WEBSITE_ENDPOINT",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "Compress": true,
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "TrustedKeyGroups": {
            "Enabled": false,
            "Quantity": 0
        },
        "MinTTL": 0
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            },
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    }
}
EOF
    )

    # Create distribution
    if ! DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config "$DIST_CONFIG" \
        --query 'Distribution.Id' \
        --output text); then
        echo "❌ Error: Failed to create CloudFront distribution"
        exit 1
    fi

    echo "   ✅ CloudFront distribution created: $DISTRIBUTION_ID"
else
    echo "   ✅ CloudFront distribution already exists: $DISTRIBUTION_ID"

    # Invalidate cache to refresh content
    echo "   🔄 Invalidating CloudFront cache..."
    if INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text); then
        echo "   ✅ Cache invalidation created: $INVALIDATION_ID"
    else
        echo "   ⚠️  Warning: Failed to invalidate cache"
    fi
fi
echo ""

# Step 6: Get distribution details
echo "📡 Getting distribution details..."
DISTRIBUTION_DOMAIN=$(aws cloudfront get-distribution \
    --id "$DISTRIBUTION_ID" \
    --query 'Distribution.DomainName' \
    --output text)

DISTRIBUTION_STATUS=$(aws cloudfront get-distribution \
    --id "$DISTRIBUTION_ID" \
    --query 'Distribution.Status' \
    --output text)

# Step 7: Create deployment metadata
echo "💾 Saving deployment metadata..."
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

mkdir -p deployments

METADATA_FILE="deployments/web-deploy-$(date +%Y%m%d-%H%M%S).json"
cat > "$METADATA_FILE" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "branch": "$BRANCH",
    "commit": "$COMMIT",
    "bucketName": "$BUCKET_NAME",
    "distributionId": "$DISTRIBUTION_ID",
    "distributionDomain": "$DISTRIBUTION_DOMAIN",
    "region": "$REGION",
    "websiteUrl": "https://$DISTRIBUTION_DOMAIN"
}
EOF

echo "   ✅ Deployment metadata saved: $METADATA_FILE"
echo ""

# Step 8: Create git tag (if in a git repo)
if git rev-parse --git-dir > /dev/null 2>&1; then
    TAG_NAME="deploy-web-$(date +%Y%m%d-%H%M%S)"
    echo "Proposed git tag: $TAG_NAME"
    read -p "Create this git tag for the deployment? (y/N): " -r
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        echo "🏷️  Creating git tag: $TAG_NAME"
        git tag -a "$TAG_NAME" -m "Web deployment to CloudFront on $TIMESTAMP"
        echo "   ✅ Git tag created"
        echo ""
        echo "   To push tag to remote:"
        echo "   git push origin $TAG_NAME"
        echo ""
    else
        echo "Skipping git tag creation."
    fi
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 S3 Bucket:           $BUCKET_NAME"
echo "☁️  CloudFront ID:       $DISTRIBUTION_ID"
echo "🌍 Website URL:         https://$DISTRIBUTION_DOMAIN"
echo "📊 Distribution Status: $DISTRIBUTION_STATUS"
echo ""

if [ "$DISTRIBUTION_STATUS" = "InProgress" ]; then
    echo "⏳ Note: CloudFront distribution is still deploying (10-15 min)"
    echo "   You can check status with: ./web-status.sh"
    echo ""
fi

echo "🔗 Direct S3 URL (for testing):"
echo "   http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"
echo ""
echo "💡 Next steps:"
echo "   1. Wait for CloudFront to deploy (if status is InProgress)"
echo "   2. Visit your website at: https://$DISTRIBUTION_DOMAIN"
echo "   3. Update backend CORS to allow: https://$DISTRIBUTION_DOMAIN"
echo "   4. (Optional) Set up custom domain in Route53"
echo ""
echo "📚 For more info, see: WEB_DEPLOYMENT.md"
echo ""
