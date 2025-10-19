
# pylint: skip-file
# flake8: noqa
# mypy: ignore-errors
# pyright: basic, reportGeneralTypeIssues=false, reportPrivateUsage=false
from unittest.mock import MagicMock, patch

from mytower.game.utilities.input import MouseState


class TestMouseState:
    """Test MouseState functionality"""

    def test_initialization(self, mock_logger_provider: MagicMock) -> None:
        """Test MouseState initialization"""
        mouse_state = MouseState(mock_logger_provider)
        
        assert mouse_state._position == (0, 0) 
        assert mouse_state._buttons == (False, False, False)
        assert mouse_state._extended_buttons == []
        assert mouse_state._wheel_y == 0
        assert mouse_state._wheel_x == 0

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_update_basic_buttons(self, mock_get_pressed: MagicMock, mock_get_pos: MagicMock, 
                                 mock_logger_provider: MagicMock) -> None:
        """Test updating mouse state with basic three buttons"""
        mock_get_pos.return_value = (100, 200)
        mock_get_pressed.return_value = [True, False, True]  # Left and right buttons pressed
        
        mouse_state = MouseState(mock_logger_provider)
        mouse_state.update()
        
        assert mouse_state.get_pos() == (100, 200)
        assert mouse_state.get_pressed() == (True, False, True)
        assert mouse_state.get_extended_pressed() == []

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_update_extended_buttons(self, mock_get_pressed: MagicMock, mock_get_pos: MagicMock, 
                                    mock_logger_provider: MagicMock) -> None:
        """Test updating mouse state with extended buttons"""
        mock_get_pos.return_value = (50, 75)
        mock_get_pressed.return_value = [False, True, False, True, False, True]  # 6 buttons
        
        mouse_state = MouseState(mock_logger_provider)
        mouse_state.update()
        
        assert mouse_state.get_pos() == (50, 75)
        assert mouse_state.get_pressed() == (False, True, False)
        assert mouse_state.get_extended_pressed() == [True, False, True]

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_update_fewer_than_three_buttons(self, mock_get_pressed: MagicMock, mock_get_pos: MagicMock, 
                                           mock_logger_provider: MagicMock) -> None:
        """Test updating mouse state when pygame returns fewer than 3 buttons"""
        mock_get_pos.return_value = (25, 50)
        mock_get_pressed.return_value = [True]  # Only one button
        
        mouse_state = MouseState(mock_logger_provider)
        mouse_state.update()
        
        assert mouse_state.get_pos() == (25, 50)
        assert mouse_state.get_pressed() == (True, False, False)
        assert mouse_state.get_extended_pressed() == []

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_update_empty_button_list(self, mock_get_pressed: MagicMock, mock_get_pos: MagicMock, 
                                     mock_logger_provider: MagicMock) -> None:
        """Test updating mouse state when pygame returns empty button list"""
        mock_get_pos.return_value = (0, 0)
        mock_get_pressed.return_value = []  # No buttons
        
        mouse_state = MouseState(mock_logger_provider)
        mouse_state.update()
        
        assert mouse_state.get_pos() == (0, 0)
        assert mouse_state.get_pressed() == (False, False, False)
        assert mouse_state.get_extended_pressed() == []

    def test_is_button_pressed_basic_buttons(self, mock_logger_provider: MagicMock) -> None:
        """Test checking if basic buttons are pressed"""
        mouse_state = MouseState(mock_logger_provider)
        mouse_state._buttons = (True, False, True)
        
        assert mouse_state.is_button_pressed(0) is True   # Left button
        assert mouse_state.is_button_pressed(1) is False  # Middle button
        assert mouse_state.is_button_pressed(2) is True   # Right button

    def test_is_button_pressed_extended_buttons(self, mock_logger_provider: MagicMock) -> None:
        """Test checking if extended buttons are pressed"""
        mouse_state = MouseState(mock_logger_provider)
        mouse_state._buttons = (False, False, False)
        mouse_state._extended_buttons = [True, False, True]
        
        # Basic buttons
        assert mouse_state.is_button_pressed(0) is False
        assert mouse_state.is_button_pressed(1) is False
        assert mouse_state.is_button_pressed(2) is False
        
        # Extended buttons
        assert mouse_state.is_button_pressed(3) is True   # First extended button
        assert mouse_state.is_button_pressed(4) is False  # Second extended button
        assert mouse_state.is_button_pressed(5) is True   # Third extended button

    def test_is_button_pressed_out_of_range(self, mock_logger_provider: MagicMock) -> None:
        """Test checking button that doesn't exist"""
        mouse_state = MouseState(mock_logger_provider)
        mouse_state._buttons = (True, False, True)
        mouse_state._extended_buttons = [False]
        
        # Check for button index that doesn't exist
        assert mouse_state.is_button_pressed(10) is False
        # Note: -1 returns True because Python allows negative indexing on tuples
        # This accesses the last element of _buttons tuple (index 2)
        assert mouse_state.is_button_pressed(-1) is True  # _buttons[2] = True

    def test_get_methods_consistency(self, mock_logger_provider: MagicMock) -> None:
        """Test that get methods return consistent data"""
        mouse_state = MouseState(mock_logger_provider)
        
        # Set some state
        mouse_state._position = (123, 456)
        mouse_state._buttons = (True, True, False)
        mouse_state._extended_buttons = [False, True]
        
        # Test consistency
        assert mouse_state.get_pos() == (123, 456)
        assert mouse_state.get_pressed() == (True, True, False)
        assert mouse_state.get_extended_pressed() == [False, True]
        
        # Multiple calls should return same values
        assert mouse_state.get_pos() == mouse_state.get_pos()
        assert mouse_state.get_pressed() == mouse_state.get_pressed()
        assert mouse_state.get_extended_pressed() == mouse_state.get_extended_pressed()

    @patch('pygame.mouse.get_pos')
    @patch('pygame.mouse.get_pressed')
    def test_multiple_updates(self, mock_get_pressed: MagicMock, mock_get_pos: MagicMock, 
                             mock_logger_provider: MagicMock) -> None:
        """Test multiple updates overwrite previous state"""
        mouse_state = MouseState(mock_logger_provider)
        
        # First update
        mock_get_pos.return_value = (10, 20)
        mock_get_pressed.return_value = [True, False, False]
        mouse_state.update()
        
        assert mouse_state.get_pos() == (10, 20)
        assert mouse_state.get_pressed() == (True, False, False)
        
        # Second update - should overwrite
        mock_get_pos.return_value = (30, 40)
        mock_get_pressed.return_value = [False, True, True]
        mouse_state.update()
        
        assert mouse_state.get_pos() == (30, 40)
        assert mouse_state.get_pressed() == (False, True, True)