# Code Review: MyTower Main Branch

**Review Date:** 2025-11-10
**Reviewer:** Claude
**Scope:** Full codebase review focusing on potential issues

## Executive Summary

This review identified **20 potential issues** across security, performance, configuration, and code quality. While the codebase demonstrates solid architecture and good practices, there are several small issues that could lead to problems in production or development environments.

**Priority Breakdown:**
- 🔴 **High Priority (Security/Reliability):** 8 issues
- 🟡 **Medium Priority (Performance/Best Practices):** 7 issues
- 🟢 **Low Priority (Code Quality/DX):** 5 issues

---

## 🔴 High Priority Issues

### 1. Missing CORS Configuration (Security)
**Location:** `mytower/api/server.py`
**Issue:** No CORS middleware configured on FastAPI server. Browser clients from different origins will be blocked.

**Impact:**
- Frontend cannot connect to API from different origin
- WebSocket connections will fail in browser
- Blocks legitimate web client access

**Suggested Fix:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Files to modify:** `mytower/api/server.py`

---

### 2. No Authentication/Authorization (Security)
**Location:** `mytower/api/schema.py`, `mytower/api/server.py`
**Issue:** GraphQL API has no authentication. Anyone can execute mutations and access game state.

**Impact:**
- Unauthorized users can modify game state
- No audit trail of who made changes
- Potential for abuse in production deployment

**Suggested Fix:**
- Add API key authentication for production
- Implement rate limiting
- Add request logging/audit trail

**Files to modify:** `mytower/api/server.py`, `mytower/api/schema.py`

---

### 3. Missing Input Validation (Security)
**Location:** `mytower/api/input_types.py`, `mytower/api/schema.py`
**Issue:** No validation on mutation inputs. Floor numbers, positions could be negative, extremely large, or invalid.

**Impact:**
- Could cause crashes or undefined behavior
- Potential for DoS by sending extreme values
- Poor error messages for users

**Example Issues:**
- `init_floor: int` - could be -999999 or 999999
- `horiz_position: Blocks` - no bounds checking
- `elevator_bank_id: str` - could be empty, malformed, or SQL injection attempt

**Suggested Fix:**
```python
from pydantic import BaseModel, field_validator
import strawberry

class AddFloorInputModel(BaseModel):
    floor_type: FloorTypeGQL
    init_floor: int
    horiz_position: int
    elevator_bank_id: str

    @field_validator("init_floor")
    @classmethod
    def floor_must_be_valid(cls, v: int) -> int:
        if v < 0 or v > 100:  # Example bounds
            raise ValueError("init_floor must be between 0 and 100")
        return v

    @field_validator("elevator_bank_id")
    @classmethod
    def bank_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("elevator_bank_id must not be empty")
        return v

@strawberry.experimental.pydantic.input(model=AddFloorInputModel, all_fields=True)
class AddFloorInput:
    pass
```

**Files to modify:** `mytower/api/input_types.py`, add validation layer

---

### 4. Unbounded Memory Growth in GameBridge (Memory Leak)
**Location:** `mytower/api/game_bridge.py:56`
**Issue:** `_command_results` dict grows unbounded. Every command result is stored forever.

```python
self._command_results: dict[str, CommandResult[Any]] = {}  # Never cleared!
```

**Impact:**
- Memory leak in long-running server
- Could eventually cause OOM in AWS deployment
- Performance degradation as dict grows

**Suggested Fix:**
- Implement LRU cache with max size
- Add periodic cleanup of old results
- Use TTL-based expiration

**Files to modify:** `mytower/api/game_bridge.py`

---

### 5. Race Condition in Hybrid Mode (Concurrency Bug)
**Location:** `mytower/main.py:268`
**Issue:** Direct controller access in hybrid mode bypasses GameBridge, causing race conditions.

```python
# TODO: These need to go on the GameBridge command queue to avoid race conditions
game_controller.set_paused(not game_controller.is_paused())
game_controller.set_speed(game_controller.speed + 0.25)
```

**Impact:**
- Potential crashes in hybrid mode
- Inconsistent game state
- Hard-to-reproduce bugs

**Suggested Fix:**
- Create commands for pause/speed changes
- Route through GameBridge command queue
- Remove direct controller access

**Files to modify:** `mytower/main.py`, `mytower/game/controllers/controller_commands.py`

---

### 6. No Graceful Shutdown (Reliability)
**Location:** `mytower/main.py`, `mytower/game/utilities/simulation_loop.py`
**Issue:** No signal handling or graceful shutdown. Game simulation thread is daemon, will be killed abruptly.

**Impact:**
- No cleanup on SIGTERM (AWS ECS task stop)
- Potential data loss
- Unclean disconnects for WebSocket clients
- Docker stop waits for timeout (10s)

**Suggested Fix:**
- Add signal handlers (SIGTERM, SIGINT)
- Implement graceful shutdown sequence
- Wait for threads to complete cleanup

**Files to modify:** `mytower/main.py`, `mytower/game/utilities/simulation_loop.py`

---

### 7. Hardcoded Server IP in Frontend (Configuration)
**Location:** `web/src/WebGameView.ts:55`
**Issue:** Server host hardcoded to `192.168.50.59`, won't work in other environments.

```typescript
const SERVER_HOST = '192.168.50.59';
```

**Impact:**
- Broken in production/local dev
- Requires code change for each environment
- Can't connect to deployed AWS instance

**Suggested Fix:**
- Use environment variables (Vite env vars)
- Default to `window.location.hostname`
- Support localhost fallback for development

**Files to modify:** `web/src/WebGameView.ts`, `web/.env.example` (create)

---

### 8. No Rate Limiting (Security/DoS)
**Location:** `mytower/api/schema.py`
**Issue:** No rate limiting on mutations or subscriptions. Single client could spam requests.

**Impact:**
- Easy DoS attack vector
- Could exhaust command queue (maxsize=10)
- Resource exhaustion in AWS

**Suggested Fix:**
- Add rate limiting middleware (slowapi)
- Limit concurrent WebSocket connections per IP
- Add backpressure to command queue

**Files to modify:** `mytower/api/server.py`, `requirements-base.txt`

---

## 🟡 Medium Priority Issues

### 9. Command Queue Fixed Size (Performance Bottleneck)
**Location:** `mytower/api/game_bridge.py:55`
**Issue:** Command queue hardcoded to maxsize=10, blocks when full.

```python
self._command_queue: Queue[tuple[str, Command[Any]]] = Queue(maxsize=10)  # TODO: Make configurable
```

**Impact:**
- GraphQL mutations can hang/timeout
- Poor scalability with multiple clients
- No visibility when queue is full

**Suggested Fix:**
- Make configurable via environment variable
- Add metrics/logging for queue size
- Consider bounded queue with reject strategy

**Files to modify:** `mytower/api/game_bridge.py`, config

---

### 10. Print Statements Instead of Logging (Code Quality)
**Location:** `mytower/api/schema.py:178, 183, 188, 223, 226, 229`
**Issue:** Subscriptions use `print()` instead of proper logging.

```python
print(f"Subscription cancelled (client likely disconnected)")
print(f"Subscription error: {e}")
```

**Impact:**
- Can't configure log levels
- No structured logging
- Difficult to parse in CloudWatch
- No log rotation

**Note:** There's even a TODO comment at line 124 about this!

**Suggested Fix:**
- Use logger from LoggerProvider
- Add structured context (client IP, subscription type)
- Remove print statements

**Files to modify:** `mytower/api/schema.py`

---

### 11. Type Ignore on Entire File (Type Safety)
**Location:** `mytower/api/unit_scalars.py:1`
**Issue:** `# type: ignore` at file level suppresses all type checking.

```python
# type: ignore
# TODO: There's some idioms in here that mypy / pyright doesn't like; fix them later.
```

**Impact:**
- Type errors hidden
- Reduced type safety
- Future bugs may go undetected

**Suggested Fix:**
- Fix underlying type issues
- Use `# type: ignore[specific-error]` on specific lines
- Enable type checking for file

**Files to modify:** `mytower/api/unit_scalars.py`

---

### 12. Inefficient Docker Health Check (Performance)
**Location:** `Dockerfile:53`, `docker-compose.yml:45`
**Issue:** Health check uses Python with urllib instead of lightweight curl.

```dockerfile
CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"
```

**Impact:**
- Slower health checks
- More resource usage
- Python startup overhead every 30s

**Suggested Fix:**
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK CMD curl -f http://localhost:8000/ || exit 1
```

**Files to modify:** `Dockerfile`, `docker-compose.yml`

---

### 13. Missing .dockerignore File (Build Performance)
**Location:** `.dockerignore` (missing)
**Issue:** No .dockerignore file means unnecessary files copied to Docker build context.

**Impact:**
- Slower builds
- Larger build context
- Potential secrets in build cache (.env, .aws, etc.)
- Cache invalidation from irrelevant changes

**Suggested Fix:**
Create `.dockerignore` with:
```
**/__pycache__
**/*.pyc
.git
.venv
venv
htmlcov
.coverage
.pytest_cache
.mypy_cache
logs/
*.log
.DS_Store
.idea
.vscode
web/node_modules
web/dist
docs/
notes/
.env*
.aws/
```

**Files to create:** `.dockerignore`

---

### 14. Inconsistent Dependency Pinning (Reproducibility)
**Location:** `requirements-base.txt`, `pyproject.toml`
**Issue:** Some packages pinned exactly, others allow any version above minimum.

```toml
# pyproject.toml
pygame>=2.5.0           # Not pinned
fastapi>=0.115.0        # Not pinned
strawberry-graphql[fastapi]>=0.245.0  # Not pinned

# requirements-base.txt
python-multipart==0.0.20  # Exact pin
python-dotenv==1.0.1      # Exact pin
```

**Impact:**
- Build reproducibility issues
- Unexpected breaking changes
- Difficult to track what versions are actually running

**Suggested Fix:**
- Generate and commit `requirements.lock` or use Poetry/pipenv
- Pin all versions in requirements files
- Use `>=x.y,<x+1.0` for semver packages

**Files to modify:** `requirements-base.txt`, `requirements-server.txt`

---

### 15. No Security Headers (Security Best Practices)
**Location:** `mytower/api/server.py`
**Issue:** No security headers (CSP, X-Frame-Options, etc.) on API responses.

**Impact:**
- Missing defense-in-depth protections
- Vulnerable to clickjacking
- No HSTS for HTTPS

**Suggested Fix:**
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

**Files to modify:** `mytower/api/server.py`

---

## 🟢 Low Priority Issues

### 16. Deployment Script Doesn't Verify Push Success (Deployment Safety)
**Location:** `deploy-backend-to-aws.sh:81-148`
**Issue:** Script creates git tag even if push might have failed, doesn't verify image is pullable.

**Impact:**
- Tags could reference unpushed images
- Confusion about what's actually deployed
- No rollback info

**Suggested Fix:**
- Verify push with `docker pull` after push
- Only tag on successful verification
- Add deployment record (JSON file with metadata)

**Files to modify:** `deploy-backend-to-aws.sh`

---

### 17. No Uvicorn Logging Configuration (Observability)
**Location:** `mytower/api/server.py:22`
**Issue:** Uvicorn uses default logging, not integrated with MyTower logging system.

```python
uvicorn.run(app, host=host, port=port)  # No log config
```

**Impact:**
- Inconsistent log format
- Can't control uvicorn log level
- No access logs in CloudWatch with context

**Suggested Fix:**
```python
log_config = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

uvicorn.run(
    app,
    host=host,
    port=port,
    log_config=log_config,
    access_log=True
)
```

**Files to modify:** `mytower/api/server.py`

---

### 18. WebSocket Error Handlers Log to Console (Consistency)
**Location:** `web/src/WebGameView.ts:66-75`
**Issue:** WebSocket errors logged to console.error, not structured.

```typescript
this.wsClient.on('error', (error: any) => {
  console.error('WebSocket connection error:', error);  // Not structured
  this.uiRenderer.showConnectionError('Connection to game server failed.');
  this.currentSnapshot = null;
});
```

**Impact:**
- Harder to monitor in production
- No error tracking integration
- Can't filter/search logs effectively

**Suggested Fix:**
- Integrate with Sentry or similar
- Add structured logging library
- Include context (server host, reconnect attempts)

**Files to modify:** `web/src/WebGameView.ts`

---

### 19. No Connection Pooling/Limits for WebSockets (Resource Management)
**Location:** `mytower/api/schema.py`
**Issue:** No global limit on concurrent WebSocket subscriptions.

**Impact:**
- Unbounded resource usage
- Potential memory exhaustion
- Poor scalability

**Suggested Fix:**
- Track active connections in GameBridge
- Implement max connection limit
- Add connection metrics
- Gracefully reject excess connections

**Files to modify:** `mytower/api/game_bridge.py`, `mytower/api/schema.py`

---

### 20. Git Ignore Has Manual Test Files (Repo Cleanliness)
**Location:** `.gitignore:162-177`
**Issue:** Hardcoded specific scratch files instead of pattern.

```
mytower/interview-sample.py
mytower/interview-sample3.py
mytower/interview-sample2.py
# ... (many specific files)
```

**Impact:**
- New scratch files not ignored
- Verbose gitignore
- Easy to accidentally commit test files

**Suggested Fix:**
```gitignore
# Scratch/test files
scratch*.py
interview-*.py
**/scratch*.py
```

**Files to modify:** `.gitignore`

---

## Suggested Commit Series

Here's a proposed series of commits to address these issues. Each commit is focused and could be implemented independently:

### Phase 1: Critical Security & Reliability (Do First)

1. **Add CORS middleware to FastAPI server**
   - Add CORSMiddleware with configurable origins
   - Add environment variable for CORS config
   - Files: `mytower/api/server.py`, `requirements-base.txt`

2. **Fix command_results memory leak in GameBridge**
   - Implement LRU cache for command_results (use collections.OrderedDict with manual size management, functools.lru_cache, or a custom implementation; if using cachetools.LRUCache, add cachetools to requirements-base.txt)
   - Add periodic cleanup task
   - Add metrics for results dict size
   - Files: `mytower/api/game_bridge.py`

3. **Add input validation to GraphQL mutations**
   - Validate floor numbers (0-100 range)
   - Validate positions (positive, reasonable bounds)
   - Validate string inputs (non-empty, max length)
   - Add proper error messages
   - Files: `mytower/api/input_types.py`, `mytower/api/schema.py`

4. **Fix race condition in hybrid mode**
   - Create SetPausedCommand and SetSpeedCommand
   - Route through GameBridge command queue
   - Remove direct controller access
   - Files: `mytower/main.py`, `mytower/game/controllers/controller_commands.py`

5. **Add graceful shutdown handling**
   - Add signal handlers (SIGTERM, SIGINT)
   - Implement shutdown event for simulation thread
   - Wait for cleanup before exit
   - Close WebSocket connections gracefully
   - Files: `mytower/main.py`, `mytower/game/utilities/simulation_loop.py`

6. **Make frontend server host configurable**
   - Use Vite environment variables
   - Default to window.location.hostname
   - Add .env.example
   - Files: `web/src/WebGameView.ts`, `web/.env.example` (new)

### Phase 2: Security & Best Practices

7. **Add rate limiting to API**
   - Install slowapi
   - Add rate limiting to mutations
   - Add connection limit for subscriptions
   - Files: `mytower/api/server.py`, `requirements-base.txt`

8. **Add security headers middleware**
   - X-Content-Type-Options
   - X-Frame-Options
   - X-XSS-Protection
   - Files: `mytower/api/server.py`

9. **Replace print statements with proper logging**
   - Use logger in subscriptions
   - Add structured context
   - Remove all print() calls
   - Files: `mytower/api/schema.py`

### Phase 3: Performance & Configuration

10. **Make command queue size configurable**
    - Add environment variable MYTOWER_COMMAND_QUEUE_SIZE
    - Add logging when queue is near full
    - Add metrics
    - Files: `mytower/api/game_bridge.py`

11. **Improve Docker health check**
    - Install curl in container
    - Replace Python health check with curl
    - Files: `Dockerfile`, `docker-compose.yml`

12. **Add .dockerignore file**
    - Exclude dev files, logs, caches
    - Improve build performance
    - Files: `.dockerignore` (new)

13. **Configure Uvicorn logging**
    - Integrate with MyTower logging system
    - Add custom log format
    - Enable access logs
    - Files: `mytower/api/server.py`

### Phase 4: Code Quality

14. **Fix type ignore in unit_scalars.py**
    - Fix underlying type issues
    - Use specific ignores only
    - Files: `mytower/api/unit_scalars.py`

15. **Pin dependency versions consistently**
    - Generate requirements.lock
    - Pin all versions
    - Add update script
    - Files: `requirements-base.txt`, `requirements-server.txt`

16. **Add WebSocket connection limits**
    - Track active subscriptions
    - Add max connection limit
    - Add connection metrics
    - Files: `mytower/api/game_bridge.py`, `mytower/api/schema.py`

17. **Improve deployment script error handling**
    - Verify image push success
    - Only tag on successful deploy
    - Add deployment metadata
    - Files: `deploy-backend-to-aws.sh`

18. **Clean up .gitignore patterns**
    - Replace specific files with patterns
    - Remove redundant entries
    - Files: `.gitignore`

### Phase 5: Future Enhancements (Optional)

19. **Add authentication/authorization**
    - Design auth strategy
    - Implement API key auth
    - Add audit logging
    - Files: Multiple

20. **Add monitoring and metrics**
    - Prometheus metrics endpoint
    - Connection/command metrics
    - Performance metrics
    - Files: Multiple

---

## Testing Recommendations

For each fix, recommend:

1. **Unit tests** for logic changes (especially validation)
2. **Integration tests** for API changes
3. **Load tests** for concurrency fixes (race conditions, queue size)
4. **Security tests** for auth/validation changes

---

## Notes

- Many of these issues are small but could compound in production
- Priority should be given to security and reliability issues
- Several issues have existing TODO comments acknowledging them
- The codebase has good architecture overall - these are polish items
- Consider adding pre-commit hooks for some checks (type checking, security scanning)

---

## Positive Observations

Worth noting - the codebase has many good qualities:
- ✅ Strong type safety with comprehensive type hints
- ✅ Good separation of concerns (MVC, Command pattern)
- ✅ Comprehensive test coverage
- ✅ Well-documented code
- ✅ Good use of protocols and abstractions
- ✅ Thread-safe design with GameBridge
- ✅ Modern Python practices (dataclasses, type hints)

These issues are relatively minor in the context of the overall code quality.
