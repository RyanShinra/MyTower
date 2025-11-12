# WebSocket Debugging - Example Logs

## Client Console Output (Browser DevTools)

### Successful Connection
```
🌐 Connecting to game server at localhost:8000
🔍 Client info: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
🔍 Page protocol: http:
🔍 WebSocket URL: ws://localhost:8000/graphql
🔌 WebSocket connecting...
✅ WebSocket opened successfully
🔍 Socket readyState: 1
🔍 Socket protocol: graphql-transport-ws
🔍 Socket url: ws://localhost:8000/graphql
✅ WebSocket connected and acknowledged
🔍 Connection payload: undefined
📡 Starting subscription to building state stream...
✅ First subscription message received!
📊 Received 100 subscription messages
📊 Received 200 subscription messages
```

### Connection Error (Server Not Running)
```
🌐 Connecting to game server at localhost:8000
🔍 Client info: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
🔍 Page protocol: http:
🔍 WebSocket URL: ws://localhost:8000/graphql
🔌 WebSocket connecting...
❌ WebSocket connection error: Event
🔍 Error type: object
🔍 Error constructor: Event
🔍 Event type: error
🔍 Event target: WebSocket
🔌 WebSocket connection closed
🔍 Close event code: 1006
🔍 Close event reason: 
🔍 Was clean: false
```

### Protocol Error (Rare)
```
🌐 Connecting to game server at localhost:8000
🔌 WebSocket connecting...
❌ WebSocket connection error: CloseEvent
🔍 Close code: 4406
🔍 Close reason: Subprotocol not acceptable
🔍 Was clean: true
```

## Server Console Output

### Startup Logs
```
2025-11-12 01:40:12,032 - mytower.api.server - INFO - 🔌 GraphQL WebSocket endpoint registered at /graphql
2025-11-12 01:40:12,033 - mytower.api.server - INFO - 📡 Supported protocols: graphql-transport-ws, graphql-ws
01:40:12.040 | INFO     | Console Log level set to INFO
01:40:12.040 | INFO     | Starting headless mode...
01:40:12.041 | INFO     | Demo building complete.
01:40:12.042 | INFO     | GraphQL server starting on http://localhost:8000/graphql
01:40:12.042 | INFO     | 🚀 Starting server on 0.0.0.0:8000
01:40:12.042 | INFO     | 🔍 WebSocket URL: ws://0.0.0.0:8000/graphql
01:40:12.042 | INFO     | 🔍 GraphQL endpoint: http://0.0.0.0:8000/graphql
INFO:     Started server process [3595]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Client Connection
```
2025-11-12 01:40:15,123 - mytower.api.server - INFO - 📨 Incoming request: GET /graphql
2025-11-12 01:40:15,123 - mytower.api.server - INFO - 🔍 Client: 127.0.0.1
2025-11-12 01:40:15,123 - mytower.api.server - INFO - 🔍 Headers: {'host': 'localhost:8000', 'connection': 'Upgrade', 'upgrade': 'websocket', 'sec-websocket-version': '13', 'sec-websocket-key': 'dGhlIHNhbXBsZSBub25jZQ==', 'sec-websocket-protocol': 'graphql-transport-ws'}
INFO:     ('127.0.0.1', 58756) - "WebSocket /graphql" [accepted]
INFO:     connection open
2025-11-12 01:40:15,124 - mytower.api.schema - INFO - 📡 New building state subscription started (interval: 50ms)
2025-11-12 01:40:15,125 - mytower.api.schema - INFO - ✅ First snapshot sent to client
```

### Client Disconnection
```
INFO:     connection closed
2025-11-12 01:40:30,456 - mytower.api.schema - INFO - 🔌 Subscription cancelled (client disconnected) - sent 300 messages
2025-11-12 01:40:30,456 - mytower.api.schema - INFO - 🧹 Building State Subscription cleaned up - total messages: 300
```

## How to Use These Logs for Debugging

### 1. Check if WebSocket Opens
Look for: `✅ WebSocket opened successfully`
- If missing → Connection refused (firewall, server not running)
- If present → Connection established

### 2. Check Protocol Negotiation
Look for: `🔍 Socket protocol: graphql-transport-ws`
- Should show `graphql-transport-ws` (modern protocol)
- If shows `graphql-ws` → Using legacy protocol (still works)
- If shows empty or different → Protocol mismatch

### 3. Check Subscription Start
Look for: `📡 Starting subscription to building state stream...`
- Should appear after connection is established
- Followed by: `✅ First subscription message received!`

### 4. Monitor Message Flow
Look for: `📊 Received X subscription messages`
- Should increment regularly (every 100 messages)
- If stuck at 0 → No data flowing
- If incrementing → Connection working

### 5. Check Server Accepts Connection
Server should log:
```
INFO:     ('127.0.0.1', XXXXX) - "WebSocket /graphql" [accepted]
INFO:     connection open
📡 New building state subscription started
✅ First snapshot sent to client
```

## Common Debugging Scenarios

### Scenario 1: "It connects but no data"
**Client logs show:**
```
✅ WebSocket connected and acknowledged
📡 Starting subscription...
(no "First subscription message received!")
```

**Possible causes:**
- Server simulation not running
- Server-side error in subscription handler
- Check server logs for errors

### Scenario 2: "Connection immediately closes"
**Client logs show:**
```
🔌 WebSocket connecting...
❌ WebSocket connection error
🔌 WebSocket connection closed
🔍 Close event code: 1006
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
