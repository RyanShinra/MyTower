# Rate Limiting and DoS Protection

## Overview
This document describes the rate limiting and DoS protection mechanisms implemented in MyTower's GraphQL API.

## Security Issues Addressed

### 1. DoS Attack Prevention
**Problem:** No rate limiting on mutations or subscriptions allowed a single client to spam requests, potentially exhausting server resources.

**Solution:** Implemented multi-layered rate limiting using `slowapi`:
- **Query Rate Limit:** 200 requests/minute per IP (configurable via `MYTOWER_RATE_LIMIT_QUERIES`)
- **Mutation Rate Limit:** 100 requests/minute per IP (configurable via `MYTOWER_RATE_LIMIT_MUTATIONS`)
- **WebSocket Connections:** 10 concurrent connections per IP (configurable via `MYTOWER_MAX_WS_CONNECTIONS`)

### 2. Command Queue Protection
**Problem:** Command queue has limited capacity (default: 100, configurable via `MYTOWER_COMMAND_QUEUE_SIZE`). A flood of mutations could exhaust the queue.

**Solution:**
- Rate limiting on mutations prevents queue exhaustion
- Added backpressure handling: mutations fail gracefully with a clear error message when queue is full
- Queue timeout added (5 seconds) to prevent indefinite blocking

### 3. WebSocket Connection Limits
**Problem:** Unlimited WebSocket connections could exhaust server resources.

**Solution:**
- Track concurrent WebSocket connections per IP address
- Reject new connections when limit is reached (returns HTTP 429)
- Automatic cleanup when connections close

## Configuration

All rate limits are configurable via environment variables:

```bash
# Query rate limit (default: 200/minute)
MYTOWER_RATE_LIMIT_QUERIES="200/minute"

# Mutation rate limit (default: 100/minute)
MYTOWER_RATE_LIMIT_MUTATIONS="100/minute"

# Max concurrent WebSocket connections per IP (default: 10)
MYTOWER_MAX_WS_CONNECTIONS="10"

# Command queue size (default: 100)
MYTOWER_COMMAND_QUEUE_SIZE="100"
```

## Rate Limit Format

Rate limits use the format: `{count}/{period}`

Examples:
- `100/minute` - 100 requests per minute
- `1000/hour` - 1000 requests per hour
- `10/second` - 10 requests per second

## Response Codes

### HTTP 429 - Too Many Requests
Returned when rate limit is exceeded. Response includes:
- `X-RateLimit-Limit` header with the limit
- `X-RateLimit-Remaining` header with remaining requests
- `X-RateLimit-Reset` header with reset timestamp

Example:
```json
{
  "error": "Rate limit exceeded: 100 per 1 minute"
}
```

### WebSocket Connection Limit
When WebSocket connection limit is reached:
```json
{
  "error": "Too many concurrent WebSocket connections",
  "limit": 10,
  "message": "Maximum 10 concurrent subscriptions per IP"
}
```

### Command Queue Full
When command queue is full:
```json
{
  "errors": [{
    "message": "Command queue is full. Server is processing commands as fast as possible. Please slow down your request rate and try again in a moment.",
    "path": ["addFloor"]
  }]
}
```

## Implementation Details

### Files Modified
1. **mytower/api/server.py**
   - Added `slowapi` rate limiting middleware
   - Implemented `RateLimitedGraphQLRouter` with WebSocket connection tracking
   - Added per-operation rate limiting (queries vs mutations)

2. **mytower/api/schema.py**
   - Updated `queue_command()` to handle `queue.Full` exceptions
   - Added timeout parameter (5 seconds default)
   - Returns clear error message when queue is full

3. **requirements-base.txt**
   - Added `slowapi>=0.1.9` for rate limiting

### Technology Stack

**slowapi Library**
- **What it is:** Rate limiting library for FastAPI (wrapper around `limits`)
- **Status:** Alpha quality, production-tested, inactive maintenance (12+ months)
- **Why chosen:** Simple human-readable limits ("100/minute"), widely used (79k weekly downloads)
- **Alternatives:**
  - `fastapi-limiter` (Redis-based, more complex setup)
  - `limits` directly (more manual integration)
  - Custom middleware (harder to differentiate query/mutation types)

### Architecture Decisions

**Why Override `__call__`?**
The `RateLimitedGraphQLRouter` overrides the `__call__` method to intercept requests before they reach Strawberry GraphQL. This is necessary because:

1. **Middleware approach:** Can't differentiate between queries and mutations without parsing
2. **FastAPI dependency:** Doesn't work well with Strawberry's router pattern
3. **Strawberry extension:** More invasive, requires modifying schema definition

The `__call__` override is industry-standard for FastAPI router customization (see `RateLimitedGraphQLRouter.__call__` in `mytower/api/server.py` for detailed explanation).

**Exception Handling Philosophy**
- **Strawberry GraphQL automatically catches exceptions** raised in resolvers
- Converts them to GraphQL error responses (NOT server crashes)
- HTTP status remains 200 (GraphQL convention) with errors in response body
- See `queue_command` function in `mytower/api/schema.py` for detailed documentation

Example error response when queue is full:
```json
{
  "data": {"addFloor": null},
  "errors": [{
    "message": "Command queue is full. Please slow down your request rate...",
    "path": ["addFloor"]
  }]
}
```

**Global Limiter Variable**
The `limiter` in `server.py` is a module-level singleton (dependency injection pattern):
```python
limiter = Limiter(key_func=get_remote_address)
```
This is standard practice for FastAPI middleware/dependencies.

**Rate Limiting Pattern**
The code uses slowapi's standard pattern (see `server.py` lines 219-229 for commented explanation):
```python
# 1. Get rate limit decorator
rate_limit_decorator: Callable = limiter.limit("100/minute")
# 2. Apply to dummy endpoint (slowapi requirement)
rate_limited_callable: Callable = rate_limit_decorator(dummy_endpoint)
# 3. Execute rate limit check
await rate_limited_callable(request)
```

### Rate Limiting Strategy

#### HTTP Requests (Queries/Mutations)
The router parses the GraphQL request body to determine operation type:
- **Mutations:** Stricter limit (100/minute) - modify state and use command queue
- **Queries:** Lenient limit (200/minute) - read-only operations
- **Unknown:** Applies mutation limit as safety measure

#### WebSocket Connections (Subscriptions)
Tracks connections per IP in a dictionary:
- Increments counter when connection opens
- Decrements counter when connection closes (in `finally` block)
- Rejects new connections when limit reached

## Testing

### Unit Tests

Comprehensive unit tests are available in `mytower/tests/api/test_rate_limiting.py`.

To run the tests:

```bash
# Run all rate limiting tests
make test -k test_rate_limiting

# Or use pytest directly
pytest mytower/tests/api/test_rate_limiting.py -v

# Run specific test class
pytest mytower/tests/api/test_rate_limiting.py::TestGraphQLRateLimiting -v
```

**Test Coverage:**
- GraphQL query rate limiting
- GraphQL mutation rate limiting
- WebSocket connection limits per IP
- Command queue backpressure handling
- Environment variable configuration
- Rate limit reset behavior
- Per-IP isolation
- Root endpoint rate limiting

### Manual Testing

1. **Test Mutation Rate Limit:**
```bash
# Send 101 mutations rapidly (should hit limit)
for i in {1..101}; do
  curl -X POST http://localhost:8000/graphql \
    -H "Content-Type: application/json" \
    -d '{"query":"mutation { addFloor(input: {floorType: LOBBY}) }"}' &
done
```

2. **Test WebSocket Limit:**
```python
import asyncio
import websockets

async def test_ws_limit():
    connections = []
    try:
        # Try to open 11 connections (should hit limit of 10)
        for i in range(11):
            ws = await websockets.connect("ws://localhost:8000/graphql")
            connections.append(ws)
            print(f"Connection {i+1} opened")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        for ws in connections:
            await ws.close()

asyncio.run(test_ws_limit())
```

3. **Test Command Queue Backpressure:**
```bash
# Set a small queue size and flood it
MYTOWER_COMMAND_QUEUE_SIZE=5 python -m mytower.api.server

# Then send many mutations rapidly
```

## Monitoring

The server logs rate limiting events:
- `🚫 Mutation rate limit exceeded for {ip}`
- `🚫 Query rate limit exceeded for {ip}`
- `🚫 WebSocket connection limit exceeded for {ip}`
- `Command queue is FULL - rejecting request (backpressure)`

Monitor these logs to:
- Detect potential DoS attacks
- Adjust rate limits based on legitimate usage patterns
- Identify clients that need to implement exponential backoff

## Best Practices

### For API Clients
1. Implement exponential backoff when receiving 429 responses
2. Limit concurrent subscriptions (respect the WebSocket connection limit)
3. Batch mutations when possible
4. Use the `building_state` query to get full state instead of many individual queries

### For Operators
1. Set `MYTOWER_COMMAND_QUEUE_SIZE` based on expected mutation rate
2. Adjust rate limits for your workload:
   - Higher for internal APIs
   - Lower for public APIs
3. Monitor queue metrics via `/health` endpoint (future enhancement)
4. Consider IP whitelisting for trusted clients (future enhancement)

## Future Enhancements

Potential improvements:
- [ ] Per-user rate limiting (instead of per-IP)
- [ ] Different rate limits for authenticated vs anonymous users
- [ ] Metrics endpoint to expose queue and rate limit stats
- [ ] Redis-based rate limiting for multi-server deployments
- [ ] Configurable rate limits per GraphQL operation
- [ ] CAPTCHA for suspicious clients
