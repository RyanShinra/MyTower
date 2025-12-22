# Updating CORS for Production

After deploying the frontend to CloudFront, you **MUST** update the backend CORS configuration to accept requests from your CloudFront domain.

## Current Configuration

The backend currently allows **all origins** (`*`) which is fine for development but should be restricted in production.

CORS is configured in `mytower/api/server.py` lines 84-106.

## How to Update CORS

### Option 1: Set Environment Variable in ECS Task Definition

1. Get your CloudFront domain from the deployment:
   ```bash
   ./web-status.sh
   # Look for the "CloudFront Distribution Domain" line
   # Example: d111111abcdef8.cloudfront.net
   ```

2. Edit `task-definition.json` and add the environment variable:
   ```json
   {
     "environment": [
       {
         "name": "MYTOWER_CORS_ORIGINS",
         "value": "https://d111111abcdef8.cloudfront.net"
       }
     ]
   }
   ```

3. Redeploy the backend:
   ```bash
   ./deploy-to-aws.sh
   ```

### Option 2: Set Environment Variable via AWS Console

1. Go to AWS ECS Console → Task Definitions → `mytower-task`
2. Create new revision
3. Find the container definition environment variables
4. Add:
   - Name: `MYTOWER_CORS_ORIGINS`
   - Value: `https://YOUR-CLOUDFRONT-DOMAIN.cloudfront.net`
5. Save and run the new task revision

### Option 3: Multiple Domains (Frontend + Local Dev)

If you want to allow both CloudFront and local development:

```json
{
  "name": "MYTOWER_CORS_ORIGINS",
  "value": "https://d111111abcdef8.cloudfront.net,http://localhost:5173"
}
```

The backend automatically parses comma-separated origins.

## Testing CORS Configuration

1. Open your browser's Developer Console (F12)
2. Navigate to your CloudFront URL
3. Try to connect to the GraphQL API
4. Check for CORS errors in the console

If you see:
```
Access to fetch at 'http://...' from origin 'https://...' has been blocked by CORS policy
```

Then CORS is not configured correctly.

## Security Note

**DO NOT use wildcard (`*`) in production!**

The current default of `*` is acceptable for:
- Development environments
- Demo deployments
- Testing

For production with real users:
- Set specific allowed origins
- Use HTTPS only (CloudFront provides this)
- Never commit CORS origins to Git if they contain internal domains

## Backend CORS Code Reference

Location: `mytower/api/server.py:84-106`

The backend reads the `MYTOWER_CORS_ORIGINS` environment variable and:
1. Splits on commas
2. Strips whitespace
3. Disables credentials if wildcard is detected (CORS security requirement)
4. Falls back to `*` if no valid origins provided

## Verification

After updating CORS, verify it's working:

```bash
# Check the task's environment variables
./aws-status.sh

# Or directly query the ECS task
aws ecs describe-tasks \
  --cluster mytower-cluster \
  --tasks $(aws ecs list-tasks --cluster mytower-cluster --query 'taskArns[0]' --output text) \
  --query 'tasks[0].containers[0].environment'
```

Look for the `MYTOWER_CORS_ORIGINS` variable in the output.
