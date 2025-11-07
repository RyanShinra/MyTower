# GraphQL WebSocket Subscriptions

MyTower now supports real-time updates via GraphQL WebSocket subscriptions! This allows clients to receive live building state updates as the game simulation runs.

## Overview

The GraphQL API provides two subscription endpoints:

1. **`buildingStateStream`** - Stream complete building state snapshots
2. **`gameTimeStream`** - Stream game time updates only (lightweight)

Both subscriptions use WebSocket connections and support configurable update intervals.

## Quick Start

### 1. Start the Server

Start MyTower in `hybrid` or `headless` mode to enable the GraphQL server:

```bash
# Hybrid mode (desktop + API server)
python -m mytower --mode hybrid

# Headless mode (API server only)
python -m mytower --mode headless
```

The GraphQL server will be available at:
- HTTP: `http://localhost:8000/graphql`
- WebSocket: `ws://localhost:8000/graphql`

### 2. Connect to Subscriptions

#### Python Client

```python
pip install gql[websockets] aiohttp
python docs/subscription_example.py
```

See [`subscription_example.py`](./subscription_example.py) for a complete example.

#### JavaScript/Node.js Client

```bash
npm install graphql-ws ws
node docs/subscription_example.js
```

See [`subscription_example.js`](./subscription_example.js) for a complete example.

## Available Subscriptions

### Building State Stream

Subscribe to complete building state updates including floors, elevators, people, money, and time.

**GraphQL Schema:**

```graphql
subscription BuildingStateStream($intervalMs: Int!) {
  buildingStateStream(intervalMs: $intervalMs) {
    time
    money
    floors {
      floorNumber
      floorType
      floorHeight
      leftEdgeBlock
      floorWidth
      personCount
      floorColor {
        r
        g
        b
      }
      floorboardColor {
        r
        g
        b
      }
    }
    elevators {
      id
      verticalPosition
      horizontalPosition
      destinationFloor
      elevatorState
      nominalDirection
      doorOpen
      passengerCount
      availableCapacity
      maxCapacity
    }
    elevatorBanks {
      id
      hCell
      minFloor
      maxFloor
      elevatorIds
    }
    people {
      personId
      currentFloorNum
      currentVerticalPosition
      currentHorizontalPosition
      destinationFloorNum
      destinationHorizontalPosition
      state
      waitingTime
      madFraction
      drawColor {
        r
        g
        b
      }
    }
  }
}
```

**Parameters:**
- `intervalMs`: Update interval in milliseconds
  - Default: `50` (~20 FPS)
  - Recommended: `50-100` for smooth updates
  - Lower values = higher update rate but more bandwidth

**Example Usage (Python):**

```python
import asyncio
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport

async def main():
    transport = WebsocketsTransport(url="ws://localhost:8000/graphql")

    async with Client(transport=transport) as session:
        subscription = gql('''
            subscription {
                buildingStateStream(intervalMs: 50) {
                    time
                    money
                    floors { floorNumber personCount }
                    elevators { id elevatorState passengerCount }
                    people { personId state madFraction }
                }
            }
        ''')

        async for result in session.subscribe(subscription):
            state = result["buildingStateStream"]
            print(f"Time: {state['time']}, Money: {state['money']}")

asyncio.run(main())
```

### Game Time Stream

Subscribe to game time updates only. This is much lighter weight than the full building state stream.

**GraphQL Schema:**

```graphql
subscription GameTimeStream($intervalMs: Int!) {
  gameTimeStream(intervalMs: $intervalMs)
}
```

**Parameters:**
- `intervalMs`: Update interval in milliseconds
  - Default: `100` (10 FPS)
  - Recommended: `100-500` for time tracking

**Example Usage (JavaScript):**

```javascript
import { createClient } from 'graphql-ws';

const client = createClient({
  url: 'ws://localhost:8000/graphql',
});

client.subscribe(
  {
    query: `
      subscription {
        gameTimeStream(intervalMs: 100)
      }
    `,
  },
  {
    next: (result) => {
      console.log('Game time:', result.data.gameTimeStream);
    },
    error: (error) => {
      console.error('Error:', error);
    },
  }
);
```

## WebSocket Protocols

The server supports both WebSocket subprotocols for maximum compatibility:

1. **`graphql-transport-ws`** (recommended) - Modern protocol with better features
2. **`graphql-ws`** (legacy) - Older protocol for backward compatibility

Most GraphQL clients will automatically select the best protocol.

## Performance Considerations

### Update Interval

- **High frequency** (50ms): Smooth real-time updates, higher bandwidth usage
- **Medium frequency** (100-200ms): Good balance for most use cases
- **Low frequency** (500ms+): Reduces bandwidth, suitable for dashboards

### Subscription Scope

- **Full building state**: Complete snapshot, larger payload
- **Game time only**: Minimal payload, use for simple time tracking
- **Future**: Filtered subscriptions (e.g., only elevators, only specific floors)

### Thread Safety

The subscription implementation uses the existing `GameBridge` which provides:
- Thread-safe snapshot access with read-write locks
- Snapshot caching (updated at 20 FPS by default)
- No blocking of game simulation thread

## Architecture

```
┌─────────────────┐
│  Game Thread    │
│  (Simulation)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   GameBridge    │  ← Thread-safe snapshot cache
│  (Snapshots)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GraphQL Schema │
│  (Subscriptions)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   WebSocket     │
│   (Transport)   │
└────────┬────────┘
         │
         ▼
    [ Clients ]
```

1. **Game Thread**: Runs the simulation and updates game state
2. **GameBridge**: Provides thread-safe snapshot access with caching
3. **GraphQL Subscriptions**: Async generators that poll the bridge
4. **WebSocket Transport**: Strawberry + FastAPI handle the WebSocket protocol
5. **Clients**: Receive real-time updates via WebSocket

## Testing with GraphiQL

You can also test subscriptions using the GraphiQL interface:

1. Open `http://localhost:8000/graphql` in your browser
2. Click on "GraphiQL" or the GraphQL playground
3. Use the subscription tab to test subscriptions
4. Example query:

```graphql
subscription {
  buildingStateStream(intervalMs: 200) {
    time
    money
    floors {
      floorNumber
      personCount
    }
  }
}
```

**Note**: Some GraphQL playground implementations may not support WebSocket subscriptions out of the box. Use a dedicated client if the playground doesn't work.

## Frontend Integration Examples

### React Hook

```typescript
import { useEffect, useState } from 'react';
import { createClient } from 'graphql-ws';

const client = createClient({
  url: 'ws://localhost:8000/graphql',
});

function useBuildingState(intervalMs = 50) {
  const [state, setState] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const unsubscribe = client.subscribe(
      {
        query: `
          subscription {
            buildingStateStream(intervalMs: ${intervalMs}) {
              time
              money
              floors { floorNumber personCount }
              elevators { id elevatorState }
            }
          }
        `,
      },
      {
        next: (result) => setState(result.data?.buildingStateStream),
        error: (err) => setError(err),
      }
    );

    return () => unsubscribe();
  }, [intervalMs]);

  return { state, error };
}
```

### Vue Composition API

```typescript
import { ref, onMounted, onUnmounted } from 'vue';
import { createClient } from 'graphql-ws';

export function useBuildingState(intervalMs = 50) {
  const buildingState = ref(null);
  const error = ref(null);
  let unsubscribe = null;

  onMounted(() => {
    const client = createClient({
      url: 'ws://localhost:8000/graphql',
    });

    unsubscribe = client.subscribe(
      {
        query: `
          subscription {
            buildingStateStream(intervalMs: ${intervalMs}) {
              time
              money
              floors { floorNumber }
            }
          }
        `,
      },
      {
        next: (result) => {
          buildingState.value = result.data?.buildingStateStream;
        },
        error: (err) => {
          error.value = err;
        },
      }
    );
  });

  onUnmounted(() => {
    if (unsubscribe) unsubscribe();
  });

  return { buildingState, error };
}
```

## Troubleshooting

### Connection Refused

**Problem**: `Connection refused` or `ECONNREFUSED`

**Solution**: Make sure the server is running in `hybrid` or `headless` mode:
```bash
python -m mytower --mode hybrid
```

### WebSocket Protocol Error

**Problem**: `WebSocket subprotocol not supported`

**Solution**: Update your GraphQL client library to the latest version. The server supports both `graphql-transport-ws` and `graphql-ws` protocols.

### No Data Streaming

**Problem**: Connected but not receiving updates

**Solution**:
1. Check that the game simulation is running (not paused)
2. Verify the subscription query syntax
3. Check server logs for errors

### High CPU Usage

**Problem**: High CPU usage with subscriptions

**Solution**:
1. Increase the `intervalMs` parameter (e.g., 100ms instead of 50ms)
2. Use `gameTimeStream` instead of `buildingStateStream` if you only need time updates
3. Limit the number of concurrent subscribers

## Future Enhancements

Potential improvements for future versions:

- [ ] **Filtered subscriptions** - Subscribe to specific entities (e.g., only floor 5)
- [ ] **Delta updates** - Stream only changes instead of full snapshots
- [ ] **Batch subscriptions** - Single WebSocket for multiple subscriptions
- [ ] **Authentication** - Secure subscriptions with authentication tokens
- [ ] **Rate limiting** - Prevent abuse with connection limits
- [ ] **Compression** - Compress payloads for reduced bandwidth

## Related Documentation

- [Protocol Architecture](./protocol_architecture.md)
- [GraphQL API Schema](../mytower/api/schema.py)
- [Game Bridge Implementation](../mytower/api/game_bridge.py)
