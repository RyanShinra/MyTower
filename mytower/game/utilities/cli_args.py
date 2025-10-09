# mytower/game/utilities/cli_args.py
"""
Command-line argument parsing for MyTower.

Supports multiple execution modes:
- Desktop: Local game with pygame rendering
- Headless: GraphQL server only (for AWS deployment)
- Hybrid: Desktop + local GraphQL server
- Remote: Desktop connected to remote server (future)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import argparse
import logging  # Add this import


@dataclass
class GameArgs:
    """
    Parsed and validated command-line arguments.
    
    Using a dataclass instead of argparse.Namespace provides:
    - Type safety
    - IDE autocomplete
    - Easier testing
    - Clear documentation of available options
    """
    mode: str  # 'desktop', 'headless', 'hybrid', 'remote'
    port: int
    demo: bool
    target_fps: int
    remote_url: Optional[str] = None
    log_level: int = logging.INFO  # Default log level
    print_exceptions: bool = False  # Whether to print full exceptions
    fail_fast: bool = False  # Whether to exit on first error
    
    def __post_init__(self) -> None:
        """Validate arguments after initialization"""
        valid_modes: set[str] = {'desktop', 'headless', 'headless_graphql', 'hybrid', 'remote'}
        if self.mode not in valid_modes:
            raise ValueError(f"Invalid mode '{self.mode}'. Must be one of {valid_modes}")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port {self.port}. Must be between 1 and 65535")
        
        if self.target_fps < 1 or self.target_fps > 240:
            raise ValueError(f"Invalid FPS {self.target_fps}. Must be between 1 and 240")
        
        if self.mode == 'remote' and not self.remote_url:
            raise ValueError("Remote mode requires --remote URL")


def parse_args() -> GameArgs:
    """
    Parse command-line arguments and return validated GameArgs.
    
    Returns:
        GameArgs with validated mode, port, and options
        
    Raises:
        SystemExit: If arguments are invalid (argparse handles this)
        ValueError: If post-validation fails
    """
    parser = argparse.ArgumentParser(
        prog='mytower',
        description='MyTower - A SimTower-inspired elevator simulation game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Run desktop game (default)
  %(prog)s --demo                       Desktop with demo building
  %(prog)s --headless                   GraphQL server only (for AWS)
  %(prog)s --headless --port 3000       GraphQL server on port 3000
  %(prog)s --with-graphql               Desktop + local GraphQL server
  %(prog)s --with-graphql --demo        Hybrid mode with demo building
  %(prog)s --remote ws://game.com       Connect to remote server (future)

Keyboard Controls (Desktop mode):
  SPACE     - Pause/unpause simulation
  UP/DOWN   - Adjust game speed
  ESC       - Exit game
        """
    )
    
    # Mutually exclusive mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--headless',
        action='store_true',
        help='Run without desktop view (GraphQL server only, for deployment)'
    )
    mode_group.add_argument(
        '--remote',
        type=str,
        metavar='URL',
        help='Connect desktop to remote server (not yet implemented)'
    )
    
    # Server options
    parser.add_argument(
        '--with-graphql',
        action='store_true',
        help='Run local GraphQL server alongside desktop view (hybrid mode)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        metavar='PORT',
        help='Port for GraphQL server (default: 8000)'
    )
    
    # Game options
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Auto-populate building with demo content (floors, elevators, people)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=60,
        metavar='FPS',
        help='Target frames per second for simulation (default: 60)'
    )
    
    # Debug/development options
    parser.add_argument(
        '--version',
        action='version',
        version='MyTower 0.1.0 (Alpha)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    parser.add_argument(
        '--print-exceptions',
        action='store_true',
        help='Print full exception stack traces for caught exceptions'
    )
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Raise exceptions instead of catching them (for debugging)'
    )
    
    args: argparse.Namespace = parser.parse_args()
    
    # Determine mode from arguments
    # Determine mode
    if args.remote:
        mode = 'remote'
        remote_url = args.remote
    elif args.headless and args.with_graphql:
        mode = 'headless_graphql'
        remote_url = None
    elif args.headless:
        mode = 'headless'
        remote_url = None
    elif args.with_graphql:
        mode = 'hybrid'
        remote_url = None
    else:
        mode = 'desktop'
        remote_url = None
    
    # Convert log level string to logging constant
    log_level_map: dict[str, int] = {
        'TRACE': 5,  # Your custom TRACE level
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level: int = log_level_map[args.log_level]
    
    # Construct and validate GameArgs
    game_args = GameArgs(
        mode=mode,
        port=args.port,
        demo=args.demo,
        target_fps=args.fps,
        remote_url=remote_url,
        log_level=log_level,
        print_exceptions=args.print_exceptions,
        fail_fast=args.fail_fast
    )
    
    return game_args


def print_startup_banner(args: GameArgs) -> None:
    """
    Print a nice startup banner showing the current mode and configuration.
    
    This helps users understand what mode they're running in, especially
    useful when launched from scripts or with complex arguments.
    """
    mode_names = {
        'desktop': 'Desktop Mode',
        'headless': 'Headless Server Mode',
        'hybrid': 'Hybrid Mode (Desktop + GraphQL)',
        'remote': 'Remote Client Mode'
    }
    
    print("=" * 60)
    print(f"  MyTower - {mode_names[args.mode]}")
    print("=" * 60)
    
    if args.mode in ('headless', 'hybrid'):
        print(f"  GraphQL Server: http://localhost:{args.port}/graphql")
    
    if args.mode == 'remote':
        print(f"  Connecting to: {args.remote_url}")
    
    if args.demo:
        print("  Demo building: ENABLED")
    
    print(f"  Simulation FPS: {args.target_fps}")
    print("=" * 60)
    print()