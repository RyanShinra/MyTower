# WebSocket Debugging - Example Logs

## Client Console Output (Browser DevTools)

### Successful Connection
```
[WEB] Connecting to game server at localhost:8000
[CHECK] Client info: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
[CHECK] Page protocol: http:
[CHECK] WebSocket URL: ws://localhost:8000/graphql
[CONNECT] WebSocket connecting...
[OK] WebSocket opened successfully
[CHECK] Socket readyState: 1
[CHECK] Socket protocol: graphql-transport-ws
[CHECK] Socket url: ws://localhost:8000/graphql
[OK] WebSocket connected and acknowledged
[CHECK] Connection payload: undefined
[SUB] Starting subscription to building state stream...
[OK] First subscription message received!
[INFO] Received 100 subscription messages
[INFO] Received 200 subscription messages
```

### Connection Error (Server Not Running)
```
[WEB] Connecting to game server at localhost:8000
[CHECK] Client info: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
[CHECK] Page protocol: http:
[CHECK] WebSocket URL: ws://localhost:8000/graphql
[CONNECT] WebSocket connecting...
[ERROR] WebSocket connection error: Event
[CHECK] Error type: object
[CHECK] Error constructor: Event
[CHECK] Event type: error
[CHECK] Event target: WebSocket
[WS] WebSocket connection closed
[CHECK] Close event code: 1006
[CHECK] Close event reason: 
[CHECK] Was clean: false
```

### Protocol Error (Rare)
```
[WEB] Connecting to game server at localhost:8000
[CONNECT] WebSocket connecting...
[ERROR] WebSocket connection error: CloseEvent
[CHECK] Close code: 4406
[CHECK] Close reason: Subprotocol not acceptable
[CHECK] Was clean: true
```

## Server Console Output

### Startup Logs
```
2025-11-12 01:40:12,032 - mytower.api.server - INFO - [WS] GraphQL WebSocket endpoint registered at /graphql
2025-11-12 01:40:12,033 - mytower.api.server - INFO - [WS] Supported protocols: graphql-transport-ws, graphql-ws
01:40:12.040 | INFO     | Console Log level set to INFO
01:40:12.040 | INFO     | Starting headless mode...
01:40:12.041 | INFO     | Demo building complete.
01:40:12.042 | INFO     | GraphQL server starting on http://localhost:8000/graphql
01:40:12.042 | INFO     | [START] Starting server on 0.0.0.0:8000
01:40:12.042 | INFO     | [CHECK] WebSocket URL: ws://0.0.0.0:8000/graphql
01:40:12.042 | INFO     | [CHECK] GraphQL endpoint: http://0.0.0.0:8000/graphql
INFO:     Started server process [3595]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Client Connection
```
2025-11-12 01:40:15,123 - mytower.api.server - INFO - [HTTP] Incoming request: GET /graphql
2025-11-12 01:40:15,123 - mytower.api.server - INFO - [CHECK] Client: 127.0.0.1
2025-11-12 01:40:15,123 - mytower.api.server - INFO - [CHECK] Headers: {'host': 'localhost:8000', 'connection': 'Upgrade', 'upgrade': 'websocket', 'sec-websocket-version': '13', 'sec-websocket-key': 'dGhlIHNhbXBsZSBub25jZQ==', 'sec-websocket-protocol': 'graphql-transport-ws'}
INFO:     ('127.0.0.1', 58756) - "WebSocket /graphql" [accepted]
INFO:     connection open
2025-11-12 01:40:15,124 - mytower.api.schema - INFO - [SUB] New building state subscription started (interval: 50ms)
2025-11-12 01:40:15,125 - mytower.api.schema - INFO - [OK] First snapshot sent to client
```

### Client Disconnection
```
INFO:     connection closed
2025-11-12 01:40:30,456 - mytower.api.schema - INFO - [SUB] Subscription cancelled (client disconnected) - sent 300 messages
2025-11-12 01:40:30,456 - mytower.api.schema - INFO - [CLEAN] Building State Subscription cleaned up - total messages: 300
```

## How to Use These Logs for Debugging

### 1. Check if WebSocket Opens
Look for: `[OK] WebSocket opened successfully`
- If missing  Connection refused (firewall, server not running)
- If present  Connection established

### 2. Check Protocol Negotiation
Look for: `[CHECK] Socket protocol: graphql-transport-ws`
- Should show `graphql-transport-ws` (modern protocol)
- If shows `graphql-ws`  Using legacy protocol (still works)
- If shows empty or different  Protocol mismatch

### 3. Check Subscription Start
Look for: `[SUB] Starting subscription to building state stream...`
- Should appear after connection is established
- Followed by: `[OK] First subscription message received!`

### 4. Monitor Message Flow
Look for: `[INFO] Received X subscription messages`
- Should increment regularly (every 100 messages)
- If stuck at 0  No data flowing
- If incrementing  Connection working

### 5. Check Server Accepts Connection
Server should log:
```
INFO:     ('127.0.0.1', XXXXX) - "WebSocket /graphql" [accepted]
INFO:     connection open
[SUB] New building state subscription started
[OK] First snapshot sent to client
```

## Common Debugging Scenarios

### Scenario 1: "It connects but no data"
**Client logs show:**
```
[OK] WebSocket connected and acknowledged
[SUB] Starting subscription...
(no "First subscription message received!")
```

**Possible causes:**
- Server simulation not running
- Server-side error in subscription handler
- Check server logs for errors

### Scenario 2: "Connection immediately closes"
**Client logs show:**
```
[CONNECT] WebSocket connecting...
[ERROR] WebSocket connection error
[WS] WebSocket connection closed
[CHECK] Close event code: 1006
```

**Possible causes:**
- Firewall blocking connection
- Server not listening on specified port
- Wrong host/port configuration

### Scenario 3: "Works on Linux, fails on Mac"
**Typical symptoms:**
- Close code: 1006 (abnormal closure)
- "Error in connection establishment"

**Mac-specific checks:**
1. Check firewall:
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   ```

2. Check if port is open:
   ```bash
   lsof -i :8000
   ```

3. Try binding to specific interface:
   ```bash
   python -m mytower.main --headless --demo
   # Server binds to 0.0.0.0:8000
   ```
