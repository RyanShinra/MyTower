# Rate Limiting Implementation Notes

## Issues Identified

### 1. **slowapi Library Concerns**
- **What is slowapi?** A wrapper around the `limits` library for FastAPI/Starlette rate limiting
- **Maturity:** Alpha quality, no releases in 12 months (inactive maintenance)
- **Usage:** Production-ready but API may change
- **Alternatives Considered:**
  - `fastapi-limiter` (Redis-based, more complex)
  - Custom implementation with `limits` directly
  - Middleware-based approach without library

**Decision:** Keep slowapi for now due to:
- Simplicity and human-readable rate formats ("100/minute")
- Production usage validation (79k weekly downloads)
- Can be replaced later if needed without changing interface

### 2. **Exception Handling Strategy**

**Problem:** Uncaught exceptions in production can crash the server.

**Original Code:**
```python
# In schema.py
raise RuntimeError("Command queue is full...")  # May crash server

# In server.py
raise  # Naked raise - unclear what's being re-raised
```

**Solution:** Use `fail_fast` flag from `GameArgs`:
- **Development (`--fail-fast`):** Raise exceptions for debugging
- **Production (default):** Log errors and return GraphQL error response

### 3. **Magic Variables and Opaque Code**

**Problems:**
1. Global `limiter` variable is "magical"
2. Chained function calls `limiter.limit(rate)(endpoint)(request)` are opaque
3. `__call__` overload without proper typing
4. Naked `raise` statements unclear

**Solutions:**
1. Document global limiter as module-level dependency injection
2. Break down chained calls with typed variables and comments
3. Fix `__call__` signature to match parent class
4. Use explicit `raise exception` (or `raise exception from None` to suppress context in the event the original is handled or you want to prevent details from leaking out via the exception stack) instead of naked `raise` 
   - Example: `raise rate_limit_error from None` is explicit and preferred over naked `raise`

### 4. **GraphQL Error Responses**

**Problem:** Rate limit should return proper GraphQL error format, not just HTTP 429.

**Solution:** slowapi's `_rate_limit_exceeded_handler` returns HTTP 429 which is correct for REST, but for GraphQL we should let Strawberry handle the error formatting.

## Refactored Approach

### Typical Exception Handling Pattern

```python
# Use fail_fast flag for exception control
try:
    # risky operation
except SomeError as e:
    if fail_fast:
        raise e  # Explicit re-raise for debugging
    else:
        logger.error(f"Error: {e}")
        return error_response  # Graceful degradation
```

Strawberry will intercept exceptions and format them as GraphQL errors. (This may still be inadequate some day), so the pattern actually used here is:
```python
# Use fail_fast flag for exception control
try:
    # risky operation
except SomeError as e:
    
        logger.error(f"Error: {e}")
        better_message = "better words"
        raise better_message from e
```
where `from e` preserves the exception stack (which you may not always want)

### Rate Limiting Clarity

```python
# BEFORE (opaque):
await limiter.limit(self.mutation_rate)(self._dummy_endpoint)(request)

# AFTER (clear):
# Get rate limit decorator from slowapi
rate_limit_decorator: Callable = limiter.limit(self.mutation_rate)
# Apply decorator to a dummy callable (slowapi requirement)
rate_limited_callable: Callable = rate_limit_decorator(self._dummy_endpoint)
# Execute the rate limit check
await rate_limited_callable(request)
```

## Alternative Implementations Considered

### Option 1: FastAPI Dependency Injection
Use FastAPI's dependency system for rate limiting:
```python
from fastapi import Depends

async def rate_limit_dependency(request: Request):
    # Check rate limit
    if exceeded:
        raise HTTPException(429)

@app.post("/graphql")
async def graphql(request: Request, _=Depends(rate_limit_dependency)):
    ...
```
**Rejected:** Doesn't work well with Strawberry's GraphQLRouter

### Option 2: Custom Middleware
Implement rate limiting as pure middleware:
```python
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Check rate limit
    # Call next
```
**Rejected:** Harder to differentiate between queries/mutations without parsing GraphQL

### Option 3: Strawberry Extensions
Use Strawberry's extension system:
```python
class RateLimitExtension(SchemaExtension):
    def on_operation(self):
        # Check rate limit
```
**Rejected:** More invasive, requires modifying schema definition

## Chosen Approach: Refined Router Overload

Keep the router overload but make it explicit and well-documented:
1. Document why we override `__call__`
2. Add proper type hints
3. Break down opaque operations
4. Use fail_fast flag
5. Add comprehensive comments

## Testing Strategy

- Mock slowapi's limiter for unit tests
- Test both fail_fast=True and fail_fast=False paths
- Verify GraphQL error format
- Test WebSocket connection tracking cleanup

## Future Improvements

1. **Metrics Collection:** Track rate limit hits for monitoring
2. **Per-User Limits:** Use authenticated user ID instead of IP
3. **Redis Backend:** For distributed rate limiting
4. **Custom Error Messages:** Per-operation error messages
5. **Gradual Backoff:** Warn before hitting limit
