# MyTower Input Architecture

## Overview

The input system is designed to be **mode-agnostic** - the same command pattern works whether playing locally or remotely.

## Component Flow

```
┌─────────────┐
│  Pygame     │
│  Events     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   InputHandler              │
│                             │
│  - Manages UI buttons       │
│  - Translates events to     │
│    commands                 │
│  - Has ONLY enqueue callback│
└──────┬──────────────────────┘
       │ queue_command(cmd)
       ▼
┌─────────────────────────────┐
│   GameBridge                │
│                             │
│  - Command queue            │
│  - Frame-based execution    │
│  - Thread-safe snapshots    │
└──────┬──────────────────────┘
       │ execute_command(cmd)
       ▼
┌─────────────────────────────┐
│   GameController            │
│                             │
│  - Validates commands       │
│  - Updates GameModel        │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   GameModel                 │
│                             │
│  - Pure business logic      │
│  - Manages entities         │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   BuildingSnapshot          │
│   (Immutable State)         │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   DesktopView               │
│                             │
│  - Pure rendering           │
│  - No game logic            │
└─────────────────────────────┘
```

## Key Design Decisions

### 1. Callback Instead of Full Bridge

```python
# ❌ BAD: Input handler has too much power
class InputHandler:
    def __init__(self, bridge: GameBridge):
        self._bridge = bridge  # Can call update_game()!

# ✅ GOOD: Input handler only has what it needs
class InputHandler:
    def __init__(self, enqueue_callback: Callable[[Command], str]):
        self._enqueue = enqueue_callback  # Can only queue commands
```

**Why?** Principle of least privilege. Input handler doesn't need (and shouldn't have) access to:
- `update_game()` - Could break frame-based execution
- `get_building_snapshot()` - View already has this
- Internal bridge state

### 2. Frame-Based Command Execution

Commands are NOT executed immediately when enqueued:

```python
# Frame N:
user clicks button → command enqueued
                  ↓
# Frame N+1:
bridge.update_game() → processes all queued commands
                    → updates model
                    → creates snapshot
view.draw()         → renders snapshot
```

**Why?** This ensures:
- Deterministic execution order
- Easy replay/networking (all mutations in one place)
- Consistent snapshots (no partial updates)

### 3. Mode Parity

The SAME input handling code works in all modes:

**Desktop Mode:**
```python
InputHandler → bridge.queue_command() → GameController
```

**Remote Mode (future):**
```python
InputHandler → network_client.send_mutation() → AWS Server → GameController
```

The input handler doesn't know or care where commands go!

## Adding New Buttons

To add a new button/command:

1. **Create the command** (in `controller_commands.py`):
```python
@dataclass
class AddElevatorBankCommand(Command[str]):
    h_cell: int
    min_floor: int
    max_floor: int

    def execute(self, model: GameModel) -> CommandResult[str]:
        bank_id = model.add_elevator_bank(...)
        return CommandResult(success=True, data=bank_id)
```

2. **Add button to InputHandler**:
```python
def _create_toolbar(self):
    # ... existing buttons ...

    add_elevator_btn = Button(
        x=button_x, y=toolbar_y,
        width=120, height=40,
        text="Add Elevator",
        ui_config=self._ui_config
    )
    self._buttons.append(add_elevator_btn)

def _on_button_clicked(self, button_index: int):
    if button_index == N:  # Your new button
        self._add_elevator_bank()

def _add_elevator_bank(self):
    command = AddElevatorBankCommand(h_cell=10, min_floor=1, max_floor=10)
    self._enqueue_command(command)
```

3. **That's it!** The command flows through the architecture automatically.

## Testing Strategy

Because input is decoupled, you can test each layer independently:

```python
# Test InputHandler without GameBridge
def test_button_click():
    commands_enqueued = []
    handler = InputHandler(enqueue_callback=commands_enqueued.append)

    # Simulate button click
    handler._on_button_clicked(0)

    assert len(commands_enqueued) == 1
    assert isinstance(commands_enqueued[0], AddFloorCommand)

# Test with mock callback
def test_floor_cycling():
    handler = InputHandler(enqueue_callback=lambda cmd: "mock-id")

    assert handler._current_floor_type == FloorType.OFFICE
    handler._add_floor()
    assert handler._current_floor_type == FloorType.APARTMENT  # Cycled
```

## Future Enhancements

### Click-to-Place
```python
def handle_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if self._placement_mode == PlacementMode.ELEVATOR:
            x, y = event.pos
            floor, block = self._screen_to_grid(x, y)
            self._enqueue_command(AddElevatorBankCommand(h_cell=block, ...))
```

### Modal Dialogs
```python
def _show_add_person_dialog(self):
    # Create modal with input fields
    # On submit, create and enqueue command
    pass
```

### Undo/Redo
```python
# GameBridge already stores command history!
def undo(self):
    # Get last command from history
    # Create inverse command
    # Enqueue it
    pass
```

## Comparison to Web UI

When you build the web frontend, it will look remarkably similar:

**Web UI (React/Vue/etc):**
```typescript
// Exact same flow, different UI toolkit
function AddFloorButton() {
    const [floorType, setFloorType] = useState('OFFICE');

    const handleClick = async () => {
        await graphqlClient.mutate({
            mutation: ADD_FLOOR,
            variables: { floorType }
        });

        // Cycle to next type (same logic!)
        setFloorType(nextFloorType(floorType));
    };

    return <button onClick={handleClick}>Add {floorType}</button>;
}
```

The desktop InputHandler becomes your **reference implementation** for how the web UI should behave!
