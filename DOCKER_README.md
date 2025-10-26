# MyTower Docker Deployment Guide

## Quick Start (Local Testing)

### 1. Build the Container
```bash
docker build -t mytower-server .
```

### 2. Run the Container
```bash
docker run -p 8000:8000 mytower-server
```

### 3. Test GraphQL
Open your browser to: http://localhost:8000/graphql

Try this query:
```graphql
query {
  hello
  isRunning
  gameTime
}
```

---

## Using Docker Compose (Recommended)

Docker Compose makes it easier to manage environment variables and volumes:

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Container Configuration

### Environment Variables
Override defaults by setting these:

- `MYTOWER_MODE` - Game mode (default: `headless`)
- `MYTOWER_PORT` - Server port (default: `8000`)
- `MYTOWER_LOG_LEVEL` - Logging level (default: `INFO`, options: `DEBUG`, `INFO`, `WARNING`, `ERROR`)

Example with custom settings:
```bash
docker run -p 8080:8080 \
  -e MYTOWER_PORT=8080 \
  -e MYTOWER_LOG_LEVEL=DEBUG \
  mytower-server
```

### Volumes
Mount the logs directory to access logs on your host:
```bash
docker run -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  mytower-server
```

---

## Development vs Production

### Development (Local)
- Use `docker-compose.yml` for easy iteration
- Logs mounted to `./logs` directory
- Debug log level enabled
- Restart on failure

### Production (AWS)
- Use standalone Dockerfile
- Logs sent to CloudWatch (AWS handles this)
- INFO log level (less verbose)
- Health checks for load balancer

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs mytower-server

# Or with compose
docker-compose logs
```

### Port already in use
```bash
# Use a different port
docker run -p 8080:8000 mytower-server
```

### Rebuild after code changes
```bash
# Force rebuild without cache
docker build --no-cache -t mytower-server .

# Or with compose
docker-compose build --no-cache
docker-compose up
```

### Check container health
```bash
# Inspect health status
docker inspect --format='{{json .State.Health}}' mytower-server

# Should show "healthy" after startup
```

---

## Image Size Optimization

The multi-stage Dockerfile keeps the image small:
- **Builder stage**: Installs build tools, compiles dependencies
- **Runtime stage**: Only copies what's needed to run

Expected image size: ~200-300 MB

To check:
```bash
docker images mytower-server
```

---

## Next Steps: AWS Deployment

Once local Docker testing works:
1. Create AWS ECR repository
2. Push image to ECR
3. Create ECS Fargate task definition
4. Deploy to ECS cluster
5. Set up Application Load Balancer
6. Configure WebSocket support

See `AWS_DEPLOYMENT.md` for detailed AWS instructions (coming next).
