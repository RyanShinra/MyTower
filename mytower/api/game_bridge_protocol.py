"""
Game Bridge Protocol for MyTower API.

Defines the interface for accessing game state in a thread-safe manner.
This protocol allows for dependency injection and testing without monkey patching.
"""

from __future__ import annotations

from typing import Protocol

from mytower.game.models.model_snapshots import BuildingSnapshot


# flake8: noqa: E704
class GameBridgeProtocol(Protocol):
    """
    Protocol defining the interface for accessing game state.

    This protocol represents the contract for thread-safe access to the game's
    current state. Implementations must provide thread-safe snapshot retrieval
    that doesn't block the game simulation thread.
    """

    def get_building_snapshot(self) -> BuildingSnapshot | None:
        """
        Get the latest building state snapshot in a thread-safe manner.

        Returns:
            BuildingSnapshot if game is running and has state, None otherwise.

        Note:
            This method must be thread-safe and non-blocking. It should return
            a cached snapshot without blocking the game simulation thread.
        """
        ...
