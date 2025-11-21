# Graceful Shutdown Implementation

## Overview

This document describes the graceful shutdown implementation for MyTower, designed to ensure clean termination when running in AWS ECS or Docker containers.

## Problem Statement

**Before this implementation:**
- No signal handling for SIGTERM/SIGINT
- Daemon threads killed abruptly on shutdown
- Infinite loops with no exit condition
- Blocking server with no programmatic shutdown
- Unclean WebSocket disconnections
- Docker container stops waited for 10-second timeout

**Impact:**
- No cleanup on AWS ECS task stop (SIGTERM)
- Potential data loss from incomplete operations
- Unclean WebSocket disconnects for clients
- Poor container orchestration behavior

## Solution Architecture

### 1. Global Shutdown Coordination (`mytower/main.py`)

**Changes:**
- Added `threading.Event()` for shutdown signaling
- Implemented signal handlers for SIGTERM and SIGINT
- Coordinated shutdown across all threads and modes

**Key Functions:**

```python
def get_shutdown_event() -> threading.Event:
    """Get or create the global shutdown event"""

def setup_signal_handlers(logger: MyTowerLogger) -> None:
    """Setup signal handlers for graceful shutdown (SIGTERM, SIGINT)"""
```

### 2. Simulation Loop Graceful Exit (`mytower/game/utilities/simulation_loop.py`)

**Changes:**
- Changed `while True` → `while shutdown_event is None or not shutdown_event.is_set()`
- Added `shutdown_event` parameter to `run_simulation_loop()`
- Made thread non-daemon when shutdown_event is provided
- Added graceful shutdown logging

**Behavior:**
- Loop exits cleanly when shutdown_event is set
- Completes current frame before exiting
- Logs shutdown with frame count
- Thread can be joined properly (non-daemon)

**Backward Compatibility:**
- `shutdown_event=None` maintains old behavior (infinite loop, daemon thread)
- Existing code without shutdown_event continues to work

### 3. Server Graceful Shutdown (`mytower/api/server.py`)

**Changes:**
- Replaced `uvicorn.run()` with `uvicorn.Server` class
- Added `run_server_async()` for async server control
- Implemented shutdown monitoring task
- Added `shutdown_event` parameter

**Implementation:**
```python
async def run_server_async(
    host: str = "127.0.0.1",
    port: int = 8000,
    shutdown_event: "threading.Event | None" = None
) -> None:
    """Run server with graceful shutdown support"""
```

**Shutdown Mechanism:**
- Background async task monitors shutdown_event
- Sets `server.should_exit = True` when triggered
- Uvicorn stops accepting connections and drains active requests
- WebSocket connections receive proper close frames

### 4. Mode-Specific Shutdown Sequences

#### Headless Mode (AWS/Docker Production)

**Shutdown Sequence:**
1. SIGTERM received → signal handler sets shutdown_event
2. Server stops accepting new connections
3. Simulation thread exits after current frame
4. Server shuts down (waits for active requests)
5. Main thread waits for simulation thread (5s timeout)
6. Clean exit

**Key Code:**
```python
# Setup signal handlers
setup_signal_handlers(logger)
shutdown_event = get_shutdown_event()

# Start non-daemon simulation thread
sim_thread = start_simulation_thread(
    bridge, logger_provider, target_fps, shutdown_event
)

# Run server with shutdown support
run_server(host="0.0.0.0", port=port, shutdown_event=shutdown_event)

# Wait for cleanup
sim_thread.join(timeout=5.0)
```

#### Desktop Mode

**Shutdown Sequence:**
1. Window close or ESC key → sets shutdown_event
2. Pygame loop exits
3. Simulation thread exits after current frame
4. Main thread waits for simulation thread (5s timeout)
5. Pygame cleanup
6. Clean exit

**Additional:** Ctrl+C in terminal also triggers shutdown via signal handler

#### Hybrid Mode (Desktop + GraphQL)

**Shutdown Sequence:**
1. Window close, ESC key, or signal → sets shutdown_event
2. Pygame loop exits
3. HTTP server stops accepting connections
4. Simulation thread exits after current frame
5. Main thread waits for simulation thread (5s timeout)
6. Main thread waits for HTTP server thread (10s timeout)
7. Pygame cleanup
8. Clean exit

**Complexity:** Coordinates 3 threads (main, simulation, HTTP server)

## Implementation Details

### Signal Handling

**Registered Signals:**
- `SIGTERM` (15): AWS ECS stop, Docker stop
- `SIGINT` (2): Ctrl+C, terminal interrupt

**Handler Behavior:**
```python
def signal_handler(signum: int, frame) -> None:
    sig_name = signal.Signals(signum).name
    logger.info(f"Received {sig_name} signal, initiating graceful shutdown...")
    shutdown_event.set()
```

### Thread Coordination

**Non-Daemon Threads:**
- When `shutdown_event` is provided, threads are non-daemon
- Allows proper joining with timeout
- Prevents abrupt termination

**Daemon Threads (Backward Compatibility):**
- When `shutdown_event=None`, threads remain daemon
- Old behavior preserved for compatibility

### Timeout Values

| Component | Timeout | Rationale |
|-----------|---------|-----------|
| Simulation Thread | 5 seconds | One frame at 60 FPS is 16ms; 5s is generous |
| HTTP Server | 10 seconds | Allows active requests to complete |
| Total Shutdown | <10 seconds | Docker default SIGKILL timeout |

### Logging

**Shutdown Events Logged:**
- Signal received (SIGTERM/SIGINT)
- Shutdown event triggered
- Simulation loop exiting with frame count
- Thread join attempts
- Thread exit status (clean vs. timeout)
- Mode-specific shutdown completion

**Example Log Output:**
```
INFO: Received SIGTERM signal, initiating graceful shutdown...
INFO: Shutdown event detected, stopping server...
INFO: Simulation loop shutting down gracefully after 1234 frames
INFO: Waiting for simulation thread to complete...
INFO: Simulation thread exited cleanly
INFO: Server stopped
INFO: Headless mode shutdown complete
```

## Testing

### Manual Testing

**Test 1a: Headless Mode SIGTERM (Direct Execution)**
```bash
# Terminal 1: Start in headless mode
python -m mytower.main --mode headless

# Terminal 2: Send SIGTERM to the process
# First, find the process ID
ps aux | grep mytower
# Then send SIGTERM
kill -TERM <process_id>

# Expected: Clean shutdown logs in Terminal 1, exit code 0
```

**Test 1b: Headless Mode SIGTERM (Docker)**
```bash
# Start Docker container
docker-compose up

# In another terminal, send SIGTERM to container
docker kill --signal=SIGTERM mytower

# Expected: Clean shutdown logs, container exits gracefully
```

**Test 2: Desktop Mode ESC Key**
```bash
# Start in desktop mode
python -m mytower.main --mode desktop

# Press ESC or close window
# Expected: Clean shutdown logs
```

**Test 3: Ctrl+C Interrupt**
```bash
# Start any mode
python -m mytower.main --mode headless

# Press Ctrl+C in the same terminal
# Expected: SIGINT caught, clean shutdown
```

### Automated Testing

**Logic Tests:**
- Shutdown event controls loop execution
- Thread daemon setting changes based on shutdown_event
- Signal handler sets event correctly
- Backward compatibility (None shutdown_event)

**Integration Tests (Future):**
- Full shutdown sequence in each mode
- Timeout handling
- Concurrent shutdowns

## AWS/Docker Benefits

### AWS ECS Task Stop

**Before:**
```
1. ECS sends SIGTERM
2. Application ignores signal
3. 30 seconds pass (configurable stopTimeout)
4. ECS sends SIGKILL
5. Abrupt termination
```

**After:**
```
1. ECS sends SIGTERM
2. Signal handler triggers shutdown
3. Clean shutdown in <10 seconds
4. Exit code 0
5. ECS marks task as stopped
```

### Docker Stop

**Before:**
```
$ docker stop mycontainer
# Waits 10 seconds
# Sends SIGKILL
# Abrupt termination
```

**After:**
```
$ docker stop mycontainer
# Receives SIGTERM
# Graceful shutdown in <10 seconds
# Clean exit
```

### Benefits

✅ **Faster deployments** - No 10-30 second wait for SIGKILL
✅ **Clean WebSocket disconnects** - Clients receive proper close frames
✅ **Data consistency** - Operations complete before shutdown
✅ **Better logging** - Clear shutdown events in logs
✅ **Container health** - Proper exit codes for orchestration
✅ **Resource cleanup** - Proper thread termination

## Configuration

### Environment Variables

No new environment variables required. Graceful shutdown works out of the box.

### Command Line Arguments

No new CLI arguments. Uses existing mode selection.

### Docker Configuration

**Recommended `docker-compose.yml`:**
```yaml
services:
  mytower:
    image: mytower:latest
    stop_grace_period: 15s  # Give 15s before SIGKILL
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

**Recommended AWS ECS Task Definition:**
```json
{
  "containerDefinitions": [{
    "name": "mytower",
    "image": "mytower:latest",
    "stopTimeout": 20,
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3
    }
  }]
}
```

## Backward Compatibility

**Preserved Behaviors:**
- Calling `start_simulation_thread()` without `shutdown_event` works as before
- Daemon thread behavior maintained when `shutdown_event=None`
- Existing tests continue to pass
- No breaking changes to public APIs

**Optional Adoption:**
- Code can gradually adopt shutdown_event
- Mixed usage is supported (daemon + non-daemon threads)

## Future Enhancements

### Potential Improvements

1. **Configurable Timeouts**
   - Environment variables for thread join timeouts
   - Different timeouts for different components

2. **Shutdown Hooks**
   - Allow custom cleanup functions
   - Pre-shutdown and post-shutdown hooks

3. **Graceful WebSocket Close**
   - Send custom close message to clients
   - "Server shutting down" notification

4. **Metrics Export on Shutdown**
   - Flush metrics before exit
   - Export final game state

5. **Health Check Integration**
   - Health endpoint returns "shutting down" during shutdown
   - Load balancers can detect and stop routing

## References

### Python Documentation
- [signal — Set handlers for asynchronous events](https://docs.python.org/3/library/signal.html)
- [threading.Event](https://docs.python.org/3/library/threading.html#event-objects)

### Uvicorn Documentation
- [Server class](https://www.uvicorn.org/deployment/#running-programmatically)
- [Graceful shutdown](https://www.uvicorn.org/deployment/#running-with-gunicorn)

### Docker Documentation
- [docker stop](https://docs.docker.com/engine/reference/commandline/stop/)
- [Stop grace period](https://docs.docker.com/compose/compose-file/#stop_grace_period)

### AWS ECS Documentation
- [Task lifecycle](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-lifecycle.html)
- [stopTimeout](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDefinition.html)

## Files Modified

### Core Implementation
- `mytower/main.py` - Signal handlers and shutdown coordination
- `mytower/game/utilities/simulation_loop.py` - Graceful loop exit
- `mytower/api/server.py` - Async server with shutdown support

### Documentation
- `docs/GRACEFUL_SHUTDOWN.md` - This document

## Summary

The graceful shutdown implementation ensures MyTower terminates cleanly in all execution modes, with special attention to AWS ECS and Docker deployment requirements. The solution:

- **Handles signals properly** (SIGTERM, SIGINT)
- **Coordinates thread shutdown** across all modes
- **Completes operations** before exit
- **Maintains backward compatibility**
- **Improves container orchestration** behavior
- **Provides clear logging** of shutdown events

This implementation is production-ready for AWS deployment and follows best practices for containerized applications.
