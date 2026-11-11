# WebSocket Connection Debugging Guide

This guide helps diagnose WebSocket connection issues between the MyTower web client and server.

## Enhanced Logging (Added)

### Client-Side Logging (Browser Console)

The web client now provides detailed WebSocket connection logs:

```
🌐 Connecting to game server at localhost:8000
🔍 Client info: Mozilla/5.0 (Macintosh; Intel Mac OS X...)
🔍 Page protocol: http:
🔍 WebSocket URL: ws://localhost:8000/graphql
🔌 WebSocket connecting...
✅ WebSocket opened successfully
🔍 Socket readyState: 1
🔍 Socket protocol: graphql-transport-ws
🔍 Socket url: ws://localhost:8000/graphql
✅ WebSocket connected and acknowledged
📡 Starting subscription to building state stream...
✅ First subscription message received!
📊 Received 100 subscription messages
```

### Server-Side Logging (Terminal/Logs)

The server now provides detailed logs for all WebSocket connections:

```
2025-11-12 01:40:12,032 - mytower.api.server - INFO - 🔌 GraphQL WebSocket endpoint registered at /graphql
2025-11-12 01:40:12,033 - mytower.api.server - INFO - 📡 Supported protocols: graphql-transport-ws, graphql-ws
01:40:12.042 | INFO     | 🚀 Starting server on 0.0.0.0:8000
01:40:12.042 | INFO     | 🔍 WebSocket URL: ws://0.0.0.0:8000/graphql
01:40:12.042 | INFO     | 🔍 GraphQL endpoint: http://0.0.0.0:8000/graphql
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2025-11-12 01:40:15,123 - mytower.api.server - INFO - 📨 Incoming request: GET /graphql
2025-11-12 01:40:15,123 - mytower.api.server - INFO - 🔍 Client: 127.0.0.1
2025-11-12 01:40:15,124 - mytower.api.schema - INFO - 📡 New building state subscription started (interval: 50ms)
2025-11-12 01:40:15,125 - mytower.api.schema - INFO - ✅ First snapshot sent to client
```

## Common Issues and Solutions

### 1. Connection Refused (Mac Firewall)

**Symptoms:**
```
❌ WebSocket connection error: Event
🔍 Event type: error
WebSocket connection to 'ws://localhost:8000/graphql' failed: Error in connection establishment
```

**Solution:**
1. Check macOS Firewall settings:
   - System Preferences → Security & Privacy → Firewall
   - Click "Firewall Options"
   - Ensure Python is allowed to accept incoming connections

2. Temporarily disable firewall to test:
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   ```
   (Re-enable after testing)

3. Check if server is listening:
   ```bash
   lsof -i :8000
   netstat -an | grep 8000
   ```

### 2. Protocol Mismatch (400 Error)

**Symptoms:**
```
❌ WebSocket connection error: CloseEvent
🔍 Close code: 4406
🔍 Close reason: Subprotocol not acceptable
```

**Solution:**
- This indicates the client and server don't support the same WebSocket subprotocol
- Both should use `graphql-transport-ws` (default in graphql-ws v6.x and Strawberry)
- Check browser console for the exact protocol being negotiated

### 3. Server Not Running

**Symptoms:**
```
WebSocket connection to 'ws://localhost:8000/graphql' failed: Error in connection establishment
🔍 Event type: error
```

**Solution:**
1. Start the server in headless or hybrid mode:
   ```bash
   python -m mytower.main --headless --demo
   # or
   python -m mytower.main --with-graphql --demo
   ```

2. Verify server is running:
   ```bash
   curl http://localhost:8000/
   # Should return: {"message":"MyTower GraphQL API","graphql":"/graphql"}
   ```

### 4. Wrong Host/Port Configuration

**Symptoms:**
- Connection attempts to wrong address
- Client logs show unexpected host/port

**Solution:**
1. Check environment variables in `web/.env`:
   ```bash
   VITE_SERVER_HOST=localhost
   VITE_SERVER_PORT=8000
   ```

2. Restart the Vite dev server after changing `.env`:
   ```bash
   npm run dev
   ```

## Debugging Workflow

### Step 1: Check Client Browser Console

Open browser DevTools (F12) and look for:
- Initial connection attempt logs (🔌 WebSocket connecting...)
- Any error messages (❌)
- Connection success messages (✅)
- Subscription message count (📊)

### Step 2: Check Server Logs

Look for:
- Server startup messages (🚀)
- Incoming WebSocket requests (📨)
- Subscription start messages (📡)
- Client disconnection messages (🔌)

### Step 3: Check Network Tab

In browser DevTools → Network tab:
1. Filter by "WS" (WebSocket)
2. Look for the `/graphql` connection
3. Check:
   - Status code (should be 101 Switching Protocols)
   - Response headers (Upgrade: websocket)
   - Messages tab (should show graphql-transport-ws protocol messages)

### Step 4: Verify Firewall/Network

On Mac:
```bash
# Check if port is open and listening
lsof -i :8000

# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Check firewall applications
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
```

### Step 5: Test Basic Connectivity

```bash
# Test HTTP endpoint
curl http://localhost:8000/

# Test WebSocket with wscat (install: npm install -g wscat)
wscat -c ws://localhost:8000/graphql -s graphql-transport-ws
```

## Logging Configuration

### Client Logging

All client logs use `console.log`, `console.warn`, and `console.error`.
- Use browser DevTools filtering to focus on specific log types
- Logs include emojis for easy visual scanning

### Server Logging

Server uses Python's `logging` module:
- Default level: INFO
- Can be adjusted with `--log-level` flag
- Logs include timestamps and logger names

To increase verbosity:
```bash
python -m mytower.main --headless --demo --log-level DEBUG
```

## Additional Resources

- [graphql-ws Documentation](https://github.com/enisdenjo/graphql-ws)
- [Strawberry GraphQL WebSocket Docs](https://strawberry.rocks/docs/general/subscriptions)
- [FastAPI WebSocket Guide](https://fastapi.tiangolo.com/advanced/websockets/)

## Contact

If you encounter issues not covered here, please open a GitHub issue with:
1. Complete client console logs
2. Complete server logs
3. Network tab screenshots
4. Your OS and browser version
5. Steps to reproduce
