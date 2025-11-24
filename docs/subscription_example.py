#!/usr/bin/env python3
# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.
"""
Example GraphQL Subscription Client for MyTower

This script demonstrates how to subscribe to real-time building state updates
via WebSocket using the GraphQL subscription API.

Requirements:
    pip install gql[websockets] aiohttp

Usage:
    1. Start the MyTower server in hybrid or headless mode:
       python -m mytower --mode hybrid

    2. Run this script:
       python docs/subscription_example.py

The script will connect to the GraphQL WebSocket endpoint and stream
building state updates in real-time.
"""

import asyncio
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport


# GraphQL subscription query for building state
BUILDING_STATE_SUBSCRIPTION = gql(
    """
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
    """
)


# GraphQL subscription query for game time only (lighter weight)
GAME_TIME_SUBSCRIPTION = gql(
    """
    subscription GameTimeStream($intervalMs: Int!) {
        gameTimeStream(intervalMs: $intervalMs)
    }
    """
)


async def subscribe_to_building_state(
    url: str = "ws://localhost:8000/graphql",
    interval_ms: int = 50,
) -> None:
    """
    Subscribe to building state updates via WebSocket.

    Args:
        url: WebSocket URL of the GraphQL endpoint
        interval_ms: Update interval in milliseconds (50ms = ~20 FPS)
    """
    # Create WebSocket transport with graphql-transport-ws protocol
    transport = WebsocketsTransport(url=url)

    # Create GraphQL client
    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        print(f"Connected to {url}")
        print(f"Streaming building state at {1000/interval_ms:.1f} FPS")
        print("-" * 60)

        # Subscribe to building state stream
        async for result in session.subscribe(
            BUILDING_STATE_SUBSCRIPTION,
            variable_values={"intervalMs": interval_ms},
        ):
            building_state = result.get("buildingStateStream")

            if building_state is None:
                print("⏸️  Game not running yet...")
                continue

            # Display building state summary
            print(f"\n⏰ Time: {building_state['time']:.1f}s | 💰 Money: ${building_state['money']}")
            print(f"🏢 Floors: {len(building_state['floors'])} | 🛗 Elevators: {len(building_state['elevators'])} | 👥 People: {len(building_state['people'])}")

            # Show elevator status
            for elevator in building_state["elevators"][:3]:  # Show first 3
                print(
                    f"  🛗 {elevator['id'][:8]}... @ {elevator['verticalPosition']:.1f} [{elevator['elevatorState']}] ({elevator['passengerCount']} passengers)" # pyright: ignore[reportImplicitStringConcatenation]
                )

            # Show people status
            mad_count = sum(1 for p in building_state["people"] if p["madFraction"] > 0.5)
            if mad_count > 0:
                print(f"  😡 {mad_count} people are getting mad!")


async def subscribe_to_game_time(
    url: str = "ws://localhost:8000/graphql",
    interval_ms: int = 100,
) -> None:
    """
    Subscribe to game time updates (lighter weight than full building state).

    Args:
        url: WebSocket URL of the GraphQL endpoint
        interval_ms: Update interval in milliseconds (100ms = 10 FPS)
    """
    transport = WebsocketsTransport(url=url)

    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        print(f"Connected to {url}")
        print(f"Streaming game time at {1000/interval_ms:.1f} FPS")
        print("-" * 60)

        async for result in session.subscribe(
            GAME_TIME_SUBSCRIPTION,
            variable_values={"intervalMs": interval_ms},
        ):
            game_time = result.get("gameTimeStream")
            print(f"⏰ Game Time: {game_time:.2f}s", end="\r")


async def main() -> None:
    """Main entry point - choose which subscription to run."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--time-only":
        # Lightweight: only stream game time
        await subscribe_to_game_time()
    else:
        # Full building state stream
        await subscribe_to_building_state(interval_ms=1000)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Subscription stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the MyTower server is running:")
        print("  python -m mytower --mode hybrid")
