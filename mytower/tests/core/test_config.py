from mytower.game.core.config import GameConfig, ElevatorConfig, ElevatorCosmetics, PersonConfig, PersonCosmetics, UIConfig
from mytower.game.core.units import Blocks, Meters  # Add unit import


class TestElevatorConfig:
    """Test ElevatorConfig dataclass"""

    def test_default_values(self) -> None:
        """Test that ElevatorConfig has expected default values"""
        config = ElevatorConfig()
        
        assert config.MAX_SPEED == 0.75
        assert config.MAX_CAPACITY == 15
        assert config.PASSENGER_LOADING_TIME == 1.0
        assert config.IDLE_WAIT_TIMEOUT == 0.5
        assert config.IDLE_LOG_TIMEOUT == 0.5
        assert config.MOVING_LOG_TIMEOUT == 0.5

    def test_immutable_constants(self) -> None:
        """Test that config constants cannot be modified"""
        config = ElevatorConfig()
        
        # These should be Final, so attempting to modify them would fail at type checking
        # But we can at least verify they exist and have the right types
        assert isinstance(config.MAX_SPEED, float)
        assert isinstance(config.MAX_CAPACITY, int)
        assert isinstance(config.PASSENGER_LOADING_TIME, float)


class TestElevatorCosmetics:
    """Test ElevatorCosmetics dataclass"""

    def test_default_values(self) -> None:
        """Test that ElevatorCosmetics has expected default values"""
        cosmetics = ElevatorCosmetics()
        
        assert cosmetics.SHAFT_COLOR == (100, 100, 100)
        assert cosmetics.SHAFT_OVERHEAD_COLOR == (24, 24, 24)
        assert cosmetics.CLOSED_COLOR == (50, 50, 200)
        assert cosmetics.OPEN_COLOR == (200, 200, 50)
        assert cosmetics.SHAFT_OVERHEAD_HEIGHT == Blocks(1.0).in_meters
        assert cosmetics.ELEVATOR_WIDTH == Blocks(1.0).in_meters

    def test_color_types(self) -> None:
        """Test that all colors are RGB tuples"""
        cosmetics = ElevatorCosmetics()
        
        for color_attr in ['SHAFT_COLOR', 'SHAFT_OVERHEAD_COLOR', 'CLOSED_COLOR', 'OPEN_COLOR']:
            color = getattr(cosmetics, color_attr)
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(isinstance(c, int) and 0 <= c <= 255 for c in color)


class TestPersonConfig:
    """Test PersonConfig dataclass"""

    def test_default_values(self) -> None:
        """Test that PersonConfig has expected default values"""
        config = PersonConfig()
        
        assert config.MAX_SPEED == 1.35  # Updated value
        assert config.WALKING_ACCELERATION == 0.5
        assert config.WALKING_DECELERATION == 0.5
        assert config.MAX_WAIT_TIME == 90.0
        assert config.IDLE_TIMEOUT == 5.0
        assert config.RADIUS == Meters(1.75)

    def test_positive_values(self) -> None:
        """Test that all config values are positive"""
        config = PersonConfig()
        
        assert config.MAX_SPEED > 0
        assert config.MAX_WAIT_TIME > 0
        assert config.IDLE_TIMEOUT > 0
        assert config.RADIUS > Meters(0)  # Compare Meters to Meters


class TestPersonCosmetics:
    """Test PersonCosmetics dataclass"""

    def test_default_values(self) -> None:
        """Test that PersonCosmetics has expected default values"""
        cosmetics = PersonCosmetics()
        
        assert cosmetics.ANGRY_MAX_RED == 192
        assert cosmetics.ANGRY_MIN_GREEN == 0
        assert cosmetics.ANGRY_MIN_BLUE == 0
        assert cosmetics.INITIAL_MAX_RED == 32
        assert cosmetics.INITIAL_MAX_GREEN == 128
        assert cosmetics.INITIAL_MAX_BLUE == 128
        assert cosmetics.INITIAL_MIN_RED == 0
        assert cosmetics.INITIAL_MIN_GREEN == 0
        assert cosmetics.INITIAL_MIN_BLUE == 0

    def test_color_ranges(self) -> None:
        """Test that color values are within valid RGB range"""
        cosmetics = PersonCosmetics()
        
        color_attrs = [
            'ANGRY_MAX_RED', 'ANGRY_MIN_GREEN', 'ANGRY_MIN_BLUE',
            'INITIAL_MAX_RED', 'INITIAL_MAX_GREEN', 'INITIAL_MAX_BLUE',
            'INITIAL_MIN_RED', 'INITIAL_MIN_GREEN', 'INITIAL_MIN_BLUE'
        ]
        
        for attr in color_attrs:
            value = getattr(cosmetics, attr)
            assert isinstance(value, int)
            assert 0 <= value <= 255


class TestUIConfig:
    """Test UIConfig dataclass"""

    def test_default_values(self) -> None:
        """Test that UIConfig has expected default values"""
        config = UIConfig()
        
        assert config.BACKGROUND_COLOR == (220, 220, 220)
        assert config.BORDER_COLOR == (150, 150, 150)
        assert config.TEXT_COLOR == (0, 0, 0)
        assert config.BUTTON_COLOR == (200, 200, 200)
        assert config.BUTTON_HOVER_COLOR == (180, 180, 180)
        assert config.UI_FONT_SIZE == 20
        assert config.FLOOR_LABEL_FONT_SIZE == 18

    def test_font_configurations(self) -> None:
        """Test font configuration types and values"""
        config = UIConfig()
        
        assert isinstance(config.UI_FONT_NAME, tuple)
        assert len(config.UI_FONT_NAME) > 0
        assert all(isinstance(font, str) for font in config.UI_FONT_NAME)
        
        assert isinstance(config.FLOOR_LABEL_FONT_NAME, tuple)
        assert len(config.FLOOR_LABEL_FONT_NAME) > 0
        assert all(isinstance(font, str) for font in config.FLOOR_LABEL_FONT_NAME)


class TestGameConfig:
    """Test GameConfig main configuration class"""

    def test_initialization(self) -> None:
        """Test that GameConfig initializes properly"""
        config = GameConfig()
        
        assert config.elevator is not None
        assert config.person is not None
        assert config.person_cosmetics is not None
        assert config.elevator_cosmetics is not None
        assert config.ui_config is not None
        assert config.initial_speed == 1.0

    def test_property_types(self) -> None:
        """Test that properties return correct types"""
        config = GameConfig()
        
        assert isinstance(config.elevator, ElevatorConfig)
        assert isinstance(config.person, PersonConfig)
        assert isinstance(config.person_cosmetics, PersonCosmetics)
        assert isinstance(config.elevator_cosmetics, ElevatorCosmetics)
        assert isinstance(config.ui_config, UIConfig)
        assert isinstance(config.initial_speed, float)

    def test_config_consistency(self) -> None:
        """Test that configurations are internally consistent"""
        config = GameConfig()
        
        # Test that speed values are reasonable
        assert config.person.MAX_SPEED < config.elevator.MAX_SPEED  # Elevators should be faster than people
        assert config.initial_speed > 0
        
        # Test that timeouts are reasonable
        assert config.elevator.IDLE_WAIT_TIMEOUT > 0
        assert config.person.IDLE_TIMEOUT > 0
        assert config.person.MAX_WAIT_TIME > config.person.IDLE_TIMEOUT  # Max wait should be longer than idle timeout

    def test_multiple_instances_independent(self) -> None:
        """Test that multiple GameConfig instances are independent"""
        config1 = GameConfig()
        config2 = GameConfig()
        
        # They should be separate objects
        assert config1 is not config2
        assert config1.elevator is not config2.elevator
        assert config1.person is not config2.person