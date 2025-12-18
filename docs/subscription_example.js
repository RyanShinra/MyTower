// Copyright (c) 2025 Ryan Osterday. All rights reserved.
// See LICENSE file for details.

/**
 * Example GraphQL Subscription Client for MyTower (JavaScript/TypeScript)
 *
 * This example demonstrates how to subscribe to real-time building state updates
 * via WebSocket using the GraphQL subscription API from a web browser or Node.js.
 *
 * Requirements (Node.js):
 *   npm install graphql-ws ws
 *
 * Requirements (Browser):
 *   npm install graphql-ws
 *
 * Usage:
 *   1. Start the MyTower server in hybrid or headless mode
 *   2. Run this script: node docs/subscription_example.js
 *   3. Or import into your frontend app
 */

// For Node.js
// const { createClient } = require('graphql-ws');
// const WebSocket = require('ws');

// For ES6 modules / TypeScript
import { createClient } from 'graphql-ws';
import WebSocket from 'ws';


// Create WebSocket client
const client = createClient({
  url: 'ws://localhost:8000/graphql',
  webSocketImpl: WebSocket, // Only needed for Node.js, omit in browser
});


// GraphQL subscription query for building state
const BUILDING_STATE_SUBSCRIPTION = `
  subscription BuildingStateStream($intervalMs: Int!) {
    buildingStateStream(intervalMs: $intervalMs) {
      time
      money
      floors {
        floorNumber
        floorType
        personCount
      }
      elevators {
        id
        verticalPosition
        elevatorState
        passengerCount
        availableCapacity
      }
      people {
        personId
        currentFloorNum
        destinationFloorNum
        state
        madFraction
      }
    }
  }
`;


// GraphQL subscription query for game time only (lighter weight)
const GAME_TIME_SUBSCRIPTION = `
  subscription GameTimeStream($intervalMs: Int!) {
    gameTimeStream(intervalMs: $intervalMs)
  }
`;


/**
 * Subscribe to building state updates
 */
function subscribeToBuildingState(intervalMs = 50) {
  console.log(` Connecting to ws://localhost:8000/graphql`);
  console.log(` Streaming building state at ${1000 / intervalMs} FPS`);
  console.log('-'.repeat(60));

  const unsubscribe = client.subscribe(
    {
      query: BUILDING_STATE_SUBSCRIPTION,
      variables: { intervalMs },
    },
    {
      next: (result) => {
        const buildingState = result.data?.buildingStateStream;

        if (!buildingState) {
          console.log('  Game not running yet...');
          return;
        }

        // Display building state summary
        console.log(`\n Time: ${buildingState.time.toFixed(1)}s |  Money: $${buildingState.money}`);
        console.log(` Floors: ${buildingState.floors.length} |  Elevators: ${buildingState.elevators.length} |  People: ${buildingState.people.length}`);

        // Show elevator status
        buildingState.elevators.slice(0, 3).forEach((elevator) => {
          console.log(
            `   ${elevator.id.substring(0, 8)}... @ ${elevator.verticalPosition.toFixed(1)} ` +
            `[${elevator.elevatorState}] (${elevator.passengerCount}/${elevator.passengerCount + elevator.availableCapacity} passengers)`
          );
        });

        // Show people status
        const madCount = buildingState.people.filter((p) => p.madFraction > 0.5).length;
        if (madCount > 0) {
          console.log(`   ${madCount} people are getting mad!`);
        }
      },
      error: (error) => {
        console.error('[ERROR] Subscription error:', error);
      },
      complete: () => {
        console.log('[OK] Subscription completed');
      },
    }
  );

  // Return unsubscribe function
  return unsubscribe;
}


/**
 * Subscribe to game time updates only (lighter weight)
 */
function subscribeToGameTime(intervalMs = 100) {
  console.log(` Connecting to ws://localhost:8000/graphql`);
  console.log(` Streaming game time at ${1000 / intervalMs} FPS`);
  console.log('-'.repeat(60));

  const unsubscribe = client.subscribe(
    {
      query: GAME_TIME_SUBSCRIPTION,
      variables: { intervalMs },
    },
    {
      next: (result) => {
        const gameTime = result.data?.gameTimeStream;
        process.stdout.write(`\r Game Time: ${gameTime?.toFixed(2)}s`);
      },
      error: (error) => {
        console.error('[ERROR] Subscription error:', error);
      },
      complete: () => {
        console.log('\n[OK] Subscription completed');
      },
    }
  );

  return unsubscribe;
}


/**
 * Example: React Hook for building state subscription
 */
/*
import { useEffect, useState } from 'react';

function useBuildingStateSubscription(intervalMs = 50) {
  const [buildingState, setBuildingState] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const unsubscribe = client.subscribe(
      {
        query: BUILDING_STATE_SUBSCRIPTION,
        variables: { intervalMs },
      },
      {
        next: (result) => {
          setBuildingState(result.data?.buildingStateStream);
        },
        error: (err) => {
          setError(err);
        },
      }
    );

    return () => {
      unsubscribe();
    };
  }, [intervalMs]);

  return { buildingState, error };
}

// Usage in component:
function BuildingDashboard() {
  const { buildingState, error } = useBuildingStateSubscription(50);

  if (error) return <div>Error: {error.message}</div>;
  if (!buildingState) return <div>Waiting for game to start...</div>;

  return (
    <div>
      <h2>Building State</h2>
      <p>Time: {buildingState.time}s</p>
      <p>Money: ${buildingState.money}</p>
      <p>Floors: {buildingState.floors.length}</p>
      <p>Elevators: {buildingState.elevators.length}</p>
      <p>People: {buildingState.people.length}</p>
    </div>
  );
}
*/


// Main entry point for Node.js
if (typeof require !== 'undefined' && require.main === module) {
  // Subscribe to building state by default
  const unsubscribe = subscribeToBuildingState(50);

  // Graceful shutdown on Ctrl+C
  process.on('SIGINT', () => {
    console.log('\n\n Stopping subscription...');
    unsubscribe();
    client.dispose();
    process.exit(0);
  });

  // Or use this for game time only:
  // const unsubscribe = subscribeToGameTime(100);
}


// Export for use in other modules
export { subscribeToBuildingState, subscribeToGameTime, client };
