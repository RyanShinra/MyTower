# mytower/game/views/input_handler.py
"""
Input handler - manages all user input (toolbar, keyboard, mouse).

Responsibilities:
- Create and manage toolbar with buttons
- Handle keyboard shortcuts
- Translate all input into game commands
- Update button states

NOT responsible for:
- Game simulation logic
- Rendering (delegates to toolbar)
"""
from typing import Callable

import pygame

from mytower.game.controllers.controller_commands import (AddFloorCommand,
                                                          AddPersonCommand,
                                                          Command)
from mytower.game.core.types import (FloorType, MouseButtons, MousePos,
                                     PygameSurface)
from mytower.game.models.model_snapshots import BuildingSnapshot
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.views.desktop_ui import Button, Toolbar, UIConfigProtocol


class InputHandler:
    """
    Manages all user input and translates it into game commands.
    
    Usage:
        handler = InputHandler(
            logger_provider,
            ui_config,
            screen_width, screen_height,
            enqueue_callback=bridge.queue_command
        )
        
        # In game loop:
        handler.handle_keyboard_event(event)  # For each pygame event
        handler.update(mouse_pos, mouse_pressed)  # Every frame
        handler.draw(surface)  # Every frame
    """
    
    def __init__(
        self,
        logger_provider: LoggerProvider,
        ui_config: UIConfigProtocol,
        screen_width: int,
        screen_height: int,
        enqueue_callback: Callable[[Command[object]], str]
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("InputHandler")
        self._logger_provider: LoggerProvider = logger_provider
        self._ui_config: UIConfigProtocol = ui_config
        self._screen_width: int = screen_width
        self._screen_height: int = screen_height
        self._enqueue_command: Callable[[Command[object]], str] = enqueue_callback
        
        # State for cycling floor types
        self._current_floor_type: FloorType = FloorType.OFFICE
        # Keep references to buttons for updating text
        self._add_floor_button: Button | None = None
        
        # Create toolbar with buttons
        self._toolbar: Toolbar = self._create_toolbar()
        
    
    # TODO: I think we may want to inject the toolbar rather than create it here...
    def _create_toolbar(self) -> Toolbar:
        """Create the toolbar and all its buttons"""
        toolbar_height = 40
        toolbar = Toolbar(
            logger_provider=self._logger_provider,
            x=0,
            # y=self._screen_height - toolbar_height,
            y=0,
            width=self._screen_width,
            height=toolbar_height,
            ui_config=self._ui_config
        )
        
        # Add Floor button
        self._add_floor_button = toolbar.add_button(
            text=f"Add {self._current_floor_type.value}",
            on_click=self._on_add_floor_clicked,
            width=180,
            height=30
        )
        
        # Add Person button
        toolbar.add_button(
            text="Add Person",
            on_click=self._on_add_person_clicked,
            width=120,
            height=30
        )
        
        return toolbar
    
    def _on_add_floor_clicked(self, snapshot: BuildingSnapshot | None) -> None:
        """Handle 'Add Floor' button click"""
        # This may come in handy later...
        if snapshot is None:
            self._logger.warning("Cannot add floor: no building snapshot available")
            return

        command = AddFloorCommand(floor_type=self._current_floor_type)
        cmd_id: str = self._enqueue_command(command)  # pyright: ignore[reportArgumentType]
        self._logger.info(
            f"Enqueued AddFloor command: {cmd_id} ({self._current_floor_type.value})"
        )
        
        # Cycle to next floor type
        self._cycle_floor_type()
        
        # Update button text
        if self._add_floor_button:
            self._add_floor_button.set_text(f"Add {self._current_floor_type.value}")

    def _on_add_person_clicked(self, snapshot: BuildingSnapshot | None) -> None:
        """Handle 'Add Person' button click"""
        import random
        
        if snapshot is None:
            self._logger.warning("Cannot add person: no building snapshot available")
            return
        # Random starting position (floor 1, random block)
        left_bounds: int = int(snapshot.floors[0].left_edge_block)
        right_bounds: int = int(snapshot.floors[0].floor_width) + left_bounds
        start_floor = 1
        start_block: float = random.uniform(left_bounds, right_bounds)
        
        # Random destination (random floor 2-10, random block)
        dest_floor: int = 1
        if len(snapshot.floors) >= 2:
            dest_floor = random.randint(2, len(snapshot.floors))
        
        dest_block: float = random.uniform(left_bounds, right_bounds)
        
        command = AddPersonCommand(
            floor=start_floor,
            block=start_block,
            dest_floor=dest_floor,
            dest_block=dest_block
        )
        cmd_id: str = self._enqueue_command(command)  # pyright: ignore[reportArgumentType]
        self._logger.info(
            f"Enqueued AddPerson command: {cmd_id} "
            f"(from floor {start_floor} to floor {dest_floor})"  # pyright: ignore[reportImplicitStringConcatenation]
        )
    
    def _cycle_floor_type(self) -> None:
        """Cycle to the next floor type"""
        floor_types: list[FloorType] = list(FloorType)
        current_index: int = floor_types.index(self._current_floor_type)
        next_index: int = (current_index + 1) % len(floor_types)
        self._current_floor_type = floor_types[next_index]

    def handle_keyboard_event(self, event: pygame.event.Event, snapshot: BuildingSnapshot | None) -> bool:
        """
        Handle a keyboard event.
        
        Returns:
            True if the event was handled, False otherwise
        """
        if event.type != pygame.KEYDOWN:  # pylint: disable=no-member
            return False
        
        # Keyboard shortcuts
        if event.key == pygame.K_f:  # pylint: disable=no-member
            self._on_add_floor_clicked(snapshot)
            return True
        elif event.key == pygame.K_p:  # pylint: disable=no-member
            self._on_add_person_clicked(snapshot)
            return True
        
        return False

    def update(self, mouse_pos: MousePos, mouse_pressed: MouseButtons, building_snapshot: BuildingSnapshot | None) -> None:
        """Update toolbar and buttons (called every frame)"""
        self._toolbar.update(mouse_pos, mouse_pressed, building_snapshot)

    def draw(self, surface: PygameSurface) -> None:
        """Draw the toolbar and all UI elements"""
        self._toolbar.draw(surface)