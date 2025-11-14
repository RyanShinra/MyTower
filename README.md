# MyTower

## Requirements

- **Python 3.13** (recommended) or Python 3.12 minimum
- Docker (for deployment)

## Why Python 3.13?

MyTower uses modern Python features and benefits significantly from 3.13's improvements:

**Performance (Critical for Real-Time Game Simulation):**
- 5-15% faster than Python 3.12
- Experimental JIT compiler (up to 30% speedup for computation-heavy tasks)
- ~7% reduced memory footprint (lower AWS costs)

**Type System (Critical for Protocol-Heavy Architecture):**
- Native `typing.override` decorator (PEP 698)
- Enhanced `typing.TypeIs` for type narrowing
- `typing.ReadOnly` for TypedDict
- Type parameter defaults
- Better variadic generics support

**Developer Experience:**
- Improved error messages with better tracebacks
- Enhanced interactive interpreter with color support
- Better debugging tools

The project's real-time simulation (~20 FPS) with elevator physics, person AI, and collision detection benefits greatly from these performance improvements.

A SimTower-inspired elevator simulation game built as a learning project for Python PCAP exam preparation.

## Architecture Highlights

- **Protocol-Driven Design**: Aggressive use of Protocol classes for type-safe duck typing
- **Interface Segregation**: Separate production and testing protocols to avoid test pollution
- **MVC Pattern**: Clean separation with Model (GameModel), View (DesktopView), Controller (GameController)
- **Command Pattern**: Type-safe mutations for replay/undo and future multiplayer support
- **Frame-Based Execution**: Deterministic game loop inspired by video game rendering patterns
- **Strong Typing**: Coming from C++/TypeScript, implemented comprehensive type hints throughout

## Deployment Goal

Headless GraphQL service on AWS for portfolio demonstration, with potential C++/Unreal Engine migration.
