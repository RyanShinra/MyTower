# MyTower Web Frontend Deployment Guide

This guide explains how to deploy the Svelte web frontend to AWS using S3 + CloudFront.

## Architecture Overview

```
                     INTERNET
                        │
                        ▼
              ┌─────────────────────┐
              │  CloudFront (CDN)   │  ← HTTPS, Global Distribution
              │  FREE TIER: 50GB/mo │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │    S3 Bucket        │  ← Static Website Hosting
              │  mytower-web-dev    │
              └─────────────────────┘
```

**Why S3 + CloudFront?**
- **Industry Standard** - Used by Netflix, Airbnb, etc.
- **Global CDN** - 450+ edge locations worldwide
- **Free HTTPS** - Automatic SSL/TLS certificates
- **Ultra Cheap** - ~$0.50/month for typical usage (free tier: $0)
- **Professional Architecture** - Shows proper separation of concerns

## Prerequisites

1. **AWS Account** with free tier
2. **AWS CLI** configured (run `aws configure`)
3. **Node.js** installed (for building the Svelte app)
4. **Bash** shell (Git Bash on Windows, native on Linux/Mac)

## Quick Start (3 Commands)

```bash
# 1. Build the Svelte frontend
./build-web.sh

# 2. Deploy to AWS (creates S3 + CloudFront)
./deploy-web-to-aws.sh

# 3. Check deployment status
./web-status.sh
```

That's it! Your website will be live at the CloudFront URL shown.

---

## Detailed Deployment Steps

### Step 1: Build the Frontend

```bash
./build-web.sh
```

**What this does:**
1. Installs npm dependencies (if needed)
2. Runs TypeScript type checking
3. Builds optimized production bundle
4. Creates `web/dist/` directory with static files

**Expected output:**
```
[BUILD] MyTower Web Frontend Build Script
=========================================

[OK]   Type checks passed
[OK]   Build completed

[INFO] Build Output:
2.5M    dist

[INFO] Files in dist/:
-rw-r--r-- 1 user user 1.5K index.html
-rw-r--r-- 1 user user 125K main.js
-rw-r--r-- 1 user user  45K style.css

[OK]   Build successful! Ready to deploy.
```

**Note:** The build script has improved cross-platform compatibility for the `du` command (works on Windows Git Bash, Linux, and Mac).

**Troubleshooting:**
- If type errors occur, fix them in `web/src/` before deploying
- If build fails, check `web/package.json` scripts
- Missing dependencies? Run `cd web && npm install`

---

### Step 2: Deploy to AWS

```bash
./deploy-web-to-aws.sh
```

**What this does:**
1. ✅ Creates S3 bucket `mytower-web-dev` (or uses existing)
2. ✅ Enables static website hosting
3. ✅ Sets public read permissions (required for websites)
4. ✅ Uploads files from `web/dist/` to S3 with optimized caching:
   - Static assets (JS, CSS, images): 1-year cache (fingerprinted URLs)
   - HTML/JSON files: No cache (always fresh)
5. ✅ Creates CloudFront distribution (or updates existing)
6. ✅ Invalidates CloudFront cache (forces refresh)
7. ✅ Creates deployment metadata in `deployments/`
8. ✅ Prompts for optional git tag `deploy-web-YYYYMMDD-HHMMSS`

**Expected output:**
```
🌐 MyTower Web Frontend Deployment to AWS
==========================================

📋 Getting AWS account info...
   ✅ Account: 123456789012
   ✅ Region: us-east-2

[INFO] Setting up S3 bucket...
[OK]   Bucket created: mytower-web-dev

[INFO] Configuring static website hosting...
[OK]   Static website hosting enabled

[INFO] Setting bucket policy for public access...
[OK]   Bucket policy configured

[INFO] Uploading files to S3...
[OK]   Files uploaded successfully

[INFO] Setting up CloudFront distribution...
[CLOUDFRONT] Distribution created: E1234567890ABC
[INFO] This takes 10-15 minutes to fully deploy

-------------------------------------------------
[WEB] Deployment Complete!
-------------------------------------------------

[S3]  Bucket:             mytower-web-dev
[CLOUDFRONT] ID:          E1234567890ABC
[URL] Website:            https://d111111abcdef8.cloudfront.net
[INFO] Distribution Status: InProgress

[INFO] Note: CloudFront distribution is still deploying (10-15 min)
[INFO] You can check status with: ./web-status.sh
```

**Important Notes:**
- ⏳ First deployment takes 10-15 minutes (CloudFront global distribution)
- 🔄 Subsequent deployments are faster (~2-3 minutes for cache invalidation)
- 💰 **100% free tier eligible** (first year, then ~$0.50/month)
- 🏷️ **Git tag is optional** - You'll be prompted whether to create a deployment tag

**Common Errors:**

**Error: Bucket name already taken**
```
[ERROR] Failed to create S3 bucket
Try adding your AWS account ID to the bucket name
```
**Solution:** Edit `deploy-web-to-aws.sh` line 11:
```bash
BUCKET_NAME=mytower-web-dev-123456789012  # Add your account ID
```

**Error: Insufficient permissions**
```
An error occurred (AccessDenied) when calling the CreateBucket operation
```
**Solution:** Your AWS user needs these IAM permissions:
- `s3:CreateBucket`
- `s3:PutBucketPolicy`
- `s3:PutBucketWebsite`
- `s3:PutObject`
- `cloudfront:CreateDistribution`
- `cloudfront:CreateInvalidation`

See "AWS Dashboard Navigation" section below for adding permissions.

---

### Step 3: Check Status

```bash
./web-status.sh
```

**What this shows:**
- ☁️ CloudFront distribution status (Deployed / InProgress)
- 🪣 S3 bucket file count and size
- 📜 Recent deployment history
- 🔄 Recent cache invalidations
- 🔗 AWS Console links for quick access

**Expected output:**
```
🌐 MyTower Web Frontend Status
==============================

[CLOUDFRONT] Distribution
[CLOUDFRONT] ━━━━━━━━━━━━━━━━━━━━━━━━━━
[CLOUDFRONT] ID:       E1234567890ABC
[CLOUDFRONT] Domain:   d111111abcdef8.cloudfront.net
[CLOUDFRONT] Status:   Deployed
[CLOUDFRONT] Enabled:  true

[URL] Website URL
[URL] https://d111111abcdef8.cloudfront.net

[S3] Bucket Status
[S3] ━━━━━━━━━━━━━━━━━━━
[S3] Name:     mytower-web-dev
[S3] Region:   us-east-2
[S3] Files:    12
[S3] Size:     2.45 MB
```

**Status Meanings:**
- `Deployed` = ✅ Website is live and accessible
- `InProgress` = ⏳ Still deploying (wait 5-10 more minutes)

---

## Updating the Website

When you make changes to the frontend code:

```bash
# 1. Make your code changes in web/src/

# 2. Rebuild
./build-web.sh

# 3. Redeploy
./deploy-web-to-aws.sh
```

The script automatically:
- Uploads new files to S3
- Invalidates CloudFront cache
- Creates new deployment record

**Cache Invalidation:**
- Happens automatically during deployment
- Manually trigger: `./web-invalidate.sh`
- Takes 1-2 minutes to propagate globally

---

## Helper Scripts Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `build-web.sh` | Build frontend (cross-platform compatible) | Before every deployment |
| `deploy-web-to-aws.sh` | Deploy to AWS (with optional git tag) | After building |
| `web-status.sh` | Check deployment status (improved file counting) | Anytime |
| `web-invalidate.sh` | Force cache refresh (better error handling) | If seeing old content |
| `web-cleanup.sh` | Delete all infrastructure (safer confirmation) | When tearing down |

### Recent Script Improvements

**Cache Optimization (`deploy-web-to-aws.sh`):**
- Static assets (JS, CSS, images) cached for 1 year (safe due to fingerprinted filenames)
- HTML/JSON files set to no-cache (ensures users always get latest content)
- Follows industry best practices for static site caching

**Cross-Platform Compatibility (`build-web.sh`):**
- Improved `du` command with fallbacks for different platforms
- Works on Windows Git Bash, Linux, and macOS

**Better Error Handling (`web-invalidate.sh`):**
- More robust error checking with proper exit codes
- Clearer error messages

**Improved File Counting (`web-status.sh`):**
- Uses `list-objects-v2` API for accurate file counts
- Handles edge cases (empty buckets, missing files)
- More portable across different environments

**Optional Git Tagging (`deploy-web-to-aws.sh`):**
- Prompts before creating git tags (y/N)
- Prevents accidental tag creation
- More flexible workflow

**Safer Cleanup (`web-cleanup.sh`):**
- Fixed string comparison (`!=` instead of `!==`)
- Clearer confirmation prompts

---

## AWS Dashboard Navigation

### How to Log In to AWS Console

1. **Go to:** https://aws.amazon.com/console/
2. **Click:** "Sign In to the Console"
3. **Enter:**
   - Account ID (or alias): `123456789012`
   - IAM username: `your-username`
   - Password: (your IAM user password)

**Forgot your account ID?**
Run: `aws sts get-caller-identity --query Account --output text`

**Forgot your username?**
Run: `aws sts get-caller-identity --query Arn --output text`
(Username is at the end: `arn:aws:iam::123456:user/YOUR-USERNAME`)

---

### Finding Your CloudFront Distribution

**Method 1: Direct Link**
Run `./web-status.sh` and click the "CloudFront:" link.

**Method 2: Manual Navigation**
1. Log in to AWS Console
2. Click the search bar at top
3. Type "CloudFront" and press Enter
4. Click "CloudFront" service
5. You'll see your distribution: "MyTower Web Frontend"

**What You'll See:**
```
┌─────────────────────────────────────────────────────────┐
│ CloudFront Distributions                                │
├─────────────────────┬───────────┬──────────┬───────────┤
│ Domain Name         │ Status    │ State    │ Comment   │
├─────────────────────┼───────────┼──────────┼───────────┤
│ d111111abcdef8....  │ Deployed  │ Enabled  │ MyTower...│
└─────────────────────┴───────────┴──────────┴───────────┘
```

**Key Tabs:**
- **General:** Shows domain name and status
- **Origins:** Shows S3 bucket connection
- **Behaviors:** Shows caching rules
- **Invalidations:** Shows cache refresh history
- **Error Pages:** Shows custom error handling (404 → index.html)

**Useful Actions:**
- **Copy Domain Name:** Right-click domain → Copy
- **Disable Distribution:** General tab → Edit → Disable
- **Create Invalidation:** Invalidations tab → Create → Path: `/*`

---

### Finding Your S3 Bucket

**Method 1: Direct Link**
Run `./web-status.sh` and click the "S3 Bucket:" link.

**Method 2: Manual Navigation**
1. Log in to AWS Console
2. Search for "S3"
3. Click "S3" service
4. Look for bucket: `mytower-web-dev`

**What You'll See:**
```
┌──────────────────────────────────────────────────────────┐
│ Buckets                                                  │
├─────────────────┬──────────┬─────────────────────────────┤
│ Name            │ Region   │ Access                      │
├─────────────────┼──────────┼─────────────────────────────┤
│ mytower-web-dev │ us-ea... │ Objects can be public       │
└─────────────────┴──────────┴─────────────────────────────┘
```

**Key Tabs (when you click the bucket):**
- **Objects:** Browse uploaded files (your website files!)
- **Properties:** Shows website hosting endpoint
- **Permissions:** Shows bucket policy (public read)
- **Management:** Shows lifecycle rules (none by default)

**Useful Actions:**
- **Upload Files:** Objects tab → Upload
- **View Website:** Properties → Static website hosting → Endpoint
- **Delete Files:** Objects tab → Select files → Delete

---

### Checking CloudFront Status (Detailed)

1. Go to CloudFront dashboard
2. Click your distribution (the domain name)
3. Look at **Status** field:
   - ✅ **Deployed** = Live and working
   - ⏳ **InProgress** = Still deploying (wait)
4. Check **Last Modified** to see when it was updated

**Distribution Details:**
```
┌───────────────────────────────────────────────────────┐
│ General                                               │
├───────────────────────────────────────────────────────┤
│ Distribution ID:      E1234567890ABC                  │
│ ARN:                  arn:aws:cloudfront::123...      │
│ Domain Name:          d111111abcdef8.cloudfront.net   │
│ Status:               Deployed ✓                      │
│ State:                Enabled                         │
│ Price Class:          Use All Edge Locations          │
│ IPv6:                 Enabled                         │
│ Last Modified:        2025-12-07 10:30:45 UTC         │
└───────────────────────────────────────────────────────┘
```

---

### Creating Cache Invalidation (Manual)

Sometimes you need to force CloudFront to refresh:

1. Go to CloudFront dashboard
2. Click your distribution
3. Click **Invalidations** tab
4. Click **Create Invalidation**
5. Enter path: `/*` (invalidates everything)
6. Click **Create Invalidation**

**What Happens:**
- Invalidation ID created (e.g., `I1234567890ABC`)
- Status shows "InProgress" → "Completed" (1-2 min)
- All edge locations clear their cache
- Next request fetches fresh files from S3

**Cost:** First 1,000 invalidations/month are FREE!

---

### Monitoring Costs

**Where to Check:**
1. AWS Console → Search "Billing"
2. Click "Billing Dashboard"
3. See current month charges

**Expected Costs (Free Tier - First 12 Months):**
- CloudFront: $0 (first 50GB data transfer out/month)
- S3: $0 (first 5GB storage, 20,000 GET requests)
- Total: **$0/month** for typical usage

**After Free Tier:**
- CloudFront: ~$0.085/GB (~$4.25 for 50GB/month)
- S3: ~$0.023/GB storage (~$0.12 for 5GB)
- Typical small website: **$0.50-$2/month**

**Setting Up Billing Alerts:**
1. Billing Dashboard → Budgets
2. Create Budget → Cost Budget
3. Set amount: $5
4. Email alert at 80% ($4)

---

### Troubleshooting in AWS Console

**Problem: Website shows 403 Forbidden**

**Solution:** Check S3 bucket permissions
1. S3 → mytower-web-dev → Permissions
2. **Block public access:** Should be OFF (all 4 toggles)
3. **Bucket policy:** Should exist with `"Effect": "Allow"`, `"Action": "s3:GetObject"`

**Problem: Website shows old content**

**Solution:** Create cache invalidation
1. CloudFront → Your distribution → Invalidations
2. Create Invalidation → Path: `/*`
3. Wait 1-2 minutes

**Problem: CloudFront stuck on "InProgress" for > 20 minutes**

**Solution:**
1. Check CloudFront → Distributions → Last Modified
2. If over 30 minutes, contact AWS Support (likely an issue on their end)
3. Try disabling and re-enabling the distribution

**Problem: Can't find my distribution**

**Solution:** Check region
1. CloudFront is **global** (no region selector)
2. If you don't see it, you might be in the wrong account
3. Run: `aws sts get-caller-identity` to check current account

---

## Connecting Frontend to Backend

After deploying, your frontend needs to talk to your backend GraphQL API.

### Step 1: Get CloudFront URL

```bash
./web-status.sh
# Copy the "Website URL" shown (e.g., https://d111111abcdef8.cloudfront.net)
```

### Step 2: Update Backend CORS

**See: `UPDATE_CORS.md` for detailed instructions**

Quick version:
```bash
# Edit task-definition.json and add:
{
  "name": "MYTOWER_CORS_ORIGINS",
  "value": "https://YOUR-CLOUDFRONT-DOMAIN.cloudfront.net"
}

# Redeploy backend
./deploy-to-aws.sh
```

### Step 3: Configure Frontend API Endpoint

Edit `web/.env` (create if it doesn't exist):
```bash
# Point to your ECS GraphQL API
VITE_SERVER_HOST=12.34.56.78  # Your ECS public IP
VITE_SERVER_PORT=8000
```

Then rebuild and redeploy:
```bash
./build-web.sh
./deploy-web-to-aws.sh
```

---

## Custom Domain Setup (Optional)

Want `mytower.example.com` instead of `d111111abcdef8.cloudfront.net`?

### Prerequisites
- Domain name (from GoDaddy, Namecheap, Route53, etc.)
- AWS Certificate Manager (ACM) SSL certificate

### Steps
1. **Request SSL Certificate (ACM)**
   - AWS Console → Certificate Manager
   - Region: **us-east-1** (CloudFront requires this)
   - Request certificate → `mytower.example.com`
   - Validate domain (DNS or email)

2. **Add Domain to CloudFront**
   - CloudFront → Your distribution → Edit
   - Alternate Domain Names (CNAMEs): `mytower.example.com`
   - SSL Certificate: Select your ACM certificate
   - Save changes

3. **Update DNS**
   - Your domain registrar (or Route53)
   - Add CNAME record:
     - Name: `mytower`
     - Value: `d111111abcdef8.cloudfront.net`

4. **Update CORS**
   - Update backend CORS to include your custom domain
   - See `UPDATE_CORS.md`

**Wait 5-10 minutes for DNS propagation, then visit:**
`https://mytower.example.com`

---

## Cleanup (Tear Down)

To delete all infrastructure:

```bash
./web-cleanup.sh
```

**This will:**
1. Disable CloudFront distribution
2. Wait for it to deploy (5 minutes)
3. Provide commands to complete deletion
4. Empty and delete S3 bucket

**Important:**
- CloudFront deletion is a 2-step process (disable → wait → delete)
- The script provides the final deletion command
- No charges after deletion (except for a few hours of partial month usage)

---

## File Structure

```
MyTower/
├── web/                          # Svelte frontend source
│   ├── src/                      # Source code
│   │   ├── App.svelte            # Main component
│   │   ├── main.ts               # Entry point
│   │   ├── WebGameView.ts        # Canvas renderer
│   │   └── rendering/            # Rendering engines
│   ├── dist/                     # Build output (created by build-web.sh)
│   ├── package.json              # Dependencies
│   └── vite.config.ts            # Build config
│
├── build-web.sh                  # Build frontend
├── deploy-web-to-aws.sh          # Deploy to S3 + CloudFront
├── web-status.sh                 # Check deployment status
├── web-invalidate.sh             # Force cache refresh
├── web-cleanup.sh                # Delete infrastructure
│
├── deployments/                  # Deployment metadata (auto-created)
│   └── web-deploy-*.json         # Deployment records
│
└── WEB_DEPLOYMENT.md             # This file
```

---

## FAQ

**Q: How much does this cost?**
A: $0/month for the first year (free tier), then ~$0.50-$2/month for typical usage.

**Q: How do I see my website?**
A: Run `./web-status.sh` and visit the URL shown.

**Q: How long does deployment take?**
A: First time: 10-15 minutes. Updates: 2-3 minutes.

**Q: Can I use my own domain?**
A: Yes! See "Custom Domain Setup" section above.

**Q: How do I update the website?**
A: Edit code → `./build-web.sh` → `./deploy-web-to-aws.sh`

**Q: What if I see old content?**
A: Run `./web-invalidate.sh` to force cache refresh.

**Q: How do I delete everything?**
A: Run `./web-cleanup.sh`

**Q: Why CloudFront instead of just S3?**
A: CloudFront adds:
- Free HTTPS/SSL
- Global CDN (faster worldwide)
- Custom domain support
- Better caching control
- Professional architecture

**Q: Can I skip CloudFront?**
A: Yes, you can use just S3 website hosting, but you lose HTTPS, global distribution, and custom domains. Not recommended for production.

**Q: What if the bucket name is taken?**
A: Bucket names are globally unique. Edit `deploy-web-to-aws.sh` line 11 and add your account ID: `mytower-web-dev-123456789012`

**Q: How do I know if it's working?**
A: Run `./web-status.sh` → if Status is "Deployed", visit the URL shown.

**Q: Do I have to create a git tag on every deployment?**
A: No! The deployment script will prompt you (y/N). You can skip it by pressing Enter or typing 'n'.

**Q: Why are my CSS/JS files cached for a year?**
A: Vite fingerprints asset filenames (e.g., `main-abc123.js`). When content changes, the filename changes, so aggressive caching is safe and improves performance.

**Q: Does this work on Windows?**
A: Yes! The scripts have been tested and work on Windows Git Bash, WSL, Linux, and macOS.

---

## Next Steps

1. ✅ Deploy frontend: `./build-web.sh && ./deploy-web-to-aws.sh`
2. ✅ Update backend CORS: See `UPDATE_CORS.md`
3. ✅ Share the CloudFront URL with others
4. ⭐ (Optional) Set up custom domain
5. ⭐ (Optional) Set up GitHub Actions for auto-deploy
6. ⭐ (Optional) Add CloudWatch monitoring

---

## Support

**Problems?**
1. Check `./web-status.sh` for current state
2. Review AWS Console (links in output)
3. Check CloudWatch Logs for backend errors
4. Review `UPDATE_CORS.md` for CORS issues

**Resources:**
- AWS S3 Static Hosting: https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html
- AWS CloudFront Guide: https://docs.aws.amazon.com/cloudfront/
- Svelte Documentation: https://svelte.dev/

---

**Built with:**
- Svelte 5.43.5
- Vite 7.2.2
- AWS S3 + CloudFront
- FastAPI + Strawberry GraphQL (backend)

**License:** See LICENSE file

---

*Last Updated: 2025-12-09 (with script improvements)*
