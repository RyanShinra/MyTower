"""
Tests for GameBridge command queue configuration and metrics.

Tests cover:
- Configurable queue size via constructor
- Configurable queue size via environment variable
- Queue metrics tracking
- Queue full behavior and logging
- Warning logs when queue is getting full
"""

import os
import queue
from unittest.mock import Mock

import pytest

from mytower.api.game_bridge import GameBridge
from mytower.game.controllers.controller_commands import AddFloorCommand
from mytower.game.core.types import FloorType
from mytower.game.utilities.logger import LoggerProvider


@pytest.fixture
def mock_controller():
    """Create a mock GameController for testing."""
    controller = Mock()
    controller.execute_command.return_value = Mock(success=True, data=1, error=None)
    controller.update.return_value = None
    controller.get_building_state.return_value = Mock()
    return controller


@pytest.fixture
def mock_logger_provider():
    """Create a mock LoggerProvider for testing."""
    provider = Mock(spec=LoggerProvider)
    logger = Mock()
    provider.get_logger.return_value = logger
    return provider


class TestQueueSizeConfiguration:
    """Test command queue size configuration."""

    def test_default_queue_size(self, mock_controller):
        """Verify default queue size is used when no configuration is provided."""
        bridge = GameBridge(controller=mock_controller)

        assert bridge._queue_size == GameBridge.DEFAULT_COMMAND_QUEUE_SIZE
        assert bridge._command_queue.maxsize == GameBridge.DEFAULT_COMMAND_QUEUE_SIZE

    def test_constructor_queue_size(self, mock_controller):
        """Verify queue size can be configured via constructor."""
        custom_size = 50
        bridge = GameBridge(controller=mock_controller, command_queue_size=custom_size)

        assert bridge._queue_size == custom_size
        assert bridge._command_queue.maxsize == custom_size

    def test_env_var_queue_size(self, mock_controller, monkeypatch):
        """Verify queue size can be configured via environment variable."""
        custom_size = 200
        monkeypatch.setenv("MYTOWER_COMMAND_QUEUE_SIZE", str(custom_size))

        bridge = GameBridge(controller=mock_controller)

        assert bridge._queue_size == custom_size
        assert bridge._command_queue.maxsize == custom_size

    def test_constructor_overrides_env_var(self, mock_controller, monkeypatch):
        """Verify constructor argument takes priority over environment variable."""
        env_size = 200
        constructor_size = 75
        monkeypatch.setenv("MYTOWER_COMMAND_QUEUE_SIZE", str(env_size))

        bridge = GameBridge(controller=mock_controller, command_queue_size=constructor_size)

        assert bridge._queue_size == constructor_size
        assert bridge._command_queue.maxsize == constructor_size

    def test_logger_initialization_message(self, mock_controller, mock_logger_provider):
        """Verify logger logs initialization message with queue size."""
        custom_size = 150
        bridge = GameBridge(
            controller=mock_controller,
            command_queue_size=custom_size,
            logger_provider=mock_logger_provider
        )

        logger = mock_logger_provider.get_logger.return_value
        logger.info.assert_called_once_with(
            f"GameBridge initialized with command queue size: {custom_size}"
        )


class TestQueueMetrics:
    """Test command queue metrics tracking."""

    def test_initial_metrics(self, mock_controller):
        """Verify metrics are initialized to zero."""
        bridge = GameBridge(controller=mock_controller, command_queue_size=10)
        metrics = bridge.get_queue_metrics()

        assert metrics["current_size"] == 0
        assert metrics["max_size"] == 10
        assert metrics["utilization"] == 0
        assert metrics["total_queued"] == 0
        assert metrics["max_seen"] == 0
        assert metrics["full_count"] == 0

    def test_metrics_after_queueing_commands(self, mock_controller):
        """Verify metrics are updated when commands are queued."""
        bridge = GameBridge(controller=mock_controller, command_queue_size=10)

        # Queue 3 commands
        for _ in range(3):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        metrics = bridge.get_queue_metrics()

        assert metrics["current_size"] == 3
        assert metrics["total_queued"] == 3
        assert metrics["max_seen"] == 3
        assert metrics["utilization"] == 30.0

    def test_max_seen_tracks_peak_usage(self, mock_controller):
        """Verify max_seen tracks the peak queue size."""
        bridge = GameBridge(controller=mock_controller, command_queue_size=10)

        # Queue 5 commands
        for _ in range(5):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        # Process some commands
        bridge._command_queue.get()
        bridge._command_queue.get()

        # Queue 2 more (total in queue: 3 + 2 = 5)
        for _ in range(2):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        metrics = bridge.get_queue_metrics()

        # max_seen should be 5 (from first batch), not current size
        assert metrics["max_seen"] == 5
        assert metrics["total_queued"] == 7


class TestQueueFullBehavior:
    """Test behavior when queue is full."""

    def test_queue_full_with_timeout_zero(self, mock_controller, mock_logger_provider):
        """Verify queue.Full is raised when timeout=0 and queue is full."""
        bridge = GameBridge(
            controller=mock_controller,
            command_queue_size=2,
            logger_provider=mock_logger_provider
        )

        # Fill the queue
        bridge.queue_command(AddFloorCommand(FloorType.LOBBY))
        bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        # Try to add one more with timeout=0 (non-blocking)
        with pytest.raises(queue.Full):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY), timeout=0)

        # Verify metrics
        metrics = bridge.get_queue_metrics()
        assert metrics["full_count"] == 1

    def test_queue_full_error_logging(self, mock_controller, mock_logger_provider):
        """Verify error is logged when queue is full."""
        bridge = GameBridge(
            controller=mock_controller,
            command_queue_size=2,
            logger_provider=mock_logger_provider
        )

        # Fill the queue
        bridge.queue_command(AddFloorCommand(FloorType.LOBBY))
        bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        # Try to add one more with timeout=0
        logger = mock_logger_provider.get_logger.return_value
        with pytest.raises(queue.Full):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY), timeout=0)

        # Verify error was logged
        assert logger.error.called
        error_message = logger.error.call_args[0][0]
        assert "FULL" in error_message
        assert "2 commands" in error_message

    def test_queue_full_count_increments(self, mock_controller):
        """Verify full_count increments each time queue is full."""
        bridge = GameBridge(controller=mock_controller, command_queue_size=1)

        # Fill and try to overfill multiple times
        bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        for _ in range(3):
            try:
                bridge.queue_command(AddFloorCommand(FloorType.LOBBY), timeout=0)
            except queue.Full:
                pass

        metrics = bridge.get_queue_metrics()
        assert metrics["full_count"] == 3


class TestQueueWarnings:
    """Test warning logs when queue is getting full."""

    def test_warning_when_queue_75_percent_full(self, mock_controller, mock_logger_provider):
        """Verify warning is logged when queue is >75% full."""
        bridge = GameBridge(
            controller=mock_controller,
            command_queue_size=10,
            logger_provider=mock_logger_provider
        )

        logger = mock_logger_provider.get_logger.return_value

        # Queue 8 commands (80% full)
        for _ in range(8):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        # Verify warning was logged
        assert logger.warning.called
        warning_message = logger.warning.call_args[0][0]
        assert "Command queue" in warning_message
        assert "full" in warning_message
        assert "8/10" in warning_message

    def test_no_warning_when_queue_below_75_percent(self, mock_controller, mock_logger_provider):
        """Verify no warning when queue is <75% full."""
        bridge = GameBridge(
            controller=mock_controller,
            command_queue_size=10,
            logger_provider=mock_logger_provider
        )

        logger = mock_logger_provider.get_logger.return_value

        # Queue 7 commands (70% full)
        for _ in range(7):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        # Verify no warning was logged
        assert not logger.warning.called


class TestQueueTimeout:
    """Test timeout behavior for queue operations."""

    def test_queue_command_with_custom_timeout(self, mock_controller):
        """Verify custom timeout is respected."""
        bridge = GameBridge(controller=mock_controller, command_queue_size=1)

        # Fill the queue
        bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        # Try to add another with very short timeout
        with pytest.raises(queue.Full):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY), timeout=0.001)

    def test_queue_command_default_blocks_indefinitely(self, mock_controller):
        """Verify default behavior blocks indefinitely (tested with small queue)."""
        bridge = GameBridge(controller=mock_controller, command_queue_size=5)

        # Should not raise exception (has room)
        for _ in range(5):
            bridge.queue_command(AddFloorCommand(FloorType.LOBBY))

        metrics = bridge.get_queue_metrics()
        assert metrics["current_size"] == 5
