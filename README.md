# MyTower

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
