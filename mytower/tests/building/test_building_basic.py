from unittest.mock import MagicMock, patch

from mytower.game.core.types import FloorType
from mytower.game.core.units import Blocks, Time  # Add import
from mytower.game.entities.building import Building
from mytower.game.entities.elevator import Elevator
from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.entities.floor import Floor


class TestBuildingBasics:
    """Test basic Building functionality"""

    def test_initialization(self, mock_logger_provider: MagicMock) -> None:
        """Test that Building initializes with correct values"""
        building = Building(mock_logger_provider, width=25)

        assert building.num_floors == 0
        assert building.building_width == Blocks(25)  # Compare to Blocks

    def test_default_width(self, mock_logger_provider: MagicMock) -> None:
        """Test Building with default width"""
        building = Building(mock_logger_provider)

        assert building.building_width == Blocks(20)  # Compare to Blocks - Default width
        assert building.num_floors == 0


    @patch("mytower.game.entities.building.Floor")
    def test_add_floor(self, mock_floor_class: MagicMock, mock_logger_provider: MagicMock) -> None:
        """Test adding floors to building"""
        building = Building(mock_logger_provider, width=30)

        # Mock the Floor constructor
        mock_floor_instance = MagicMock(spec=Floor)
        mock_floor_class.return_value = mock_floor_instance

        # Add first floor
        floor_num = building.add_floor(FloorType.LOBBY)
        assert floor_num == 1
        assert building.num_floors == 1

        # Verify Floor was constructed correctly
        mock_floor_class.assert_called_with(
            mock_logger_provider,
            building,
            1,  # floor_num
            FloorType.LOBBY,
            Blocks(0),  # left_edge - now Blocks
            Blocks(30),  # building width - now Blocks
        )

        # Add second floor
        floor_num = building.add_floor(FloorType.OFFICE)
        assert floor_num == 2
        assert building.num_floors == 2


    def test_add_elevator_bank(self, mock_logger_provider: MagicMock) -> None:
        """Test adding elevator banks to building"""
        building = Building(mock_logger_provider)

        mock_bank1 = MagicMock(spec=ElevatorBank)
        mock_bank2 = MagicMock(spec=ElevatorBank)

        building.add_elevator_bank(mock_bank1)
        assert len(building.get_elevator_banks()) == 1
        assert mock_bank1 in building.get_elevator_banks()

        building.add_elevator_bank(mock_bank2)
        assert len(building.get_elevator_banks()) == 2
        assert mock_bank2 in building.get_elevator_banks()

    # test_add_person removed as Building no longer manages people directly
class TestBuildingFloorRetrieval:
    """Test floor retrieval methods"""


    @patch("mytower.game.entities.building.Floor")
    def test_get_floors(self, mock_floor_class: MagicMock, mock_logger_provider: MagicMock) -> None:
        """Test getting all floors in order"""
        building = Building(mock_logger_provider)

        # Create mock floors
        mock_floors = []
        for _i in range(3):  # Prefix with underscore to mark as intentionally unused
            mock_floor = MagicMock(spec=Floor)
            mock_floors.append(mock_floor)
            mock_floor_class.return_value = mock_floor
            building.add_floor(FloorType.OFFICE)
            mock_floor_class.return_value = MagicMock(spec=Floor)  # Reset for next iteration

        floors = building.get_floors()
        assert len(floors) == 3
        # Should return floors in order from 1 to num_floors
    @patch("mytower.game.entities.building.Floor")
    def test_get_floor_by_number(self, mock_floor_class: MagicMock, mock_logger_provider: MagicMock) -> None:
        """Test getting floor by specific number"""
        building = Building(mock_logger_provider)

        mock_floor1 = MagicMock(spec=Floor)
        mock_floor2 = MagicMock(spec=Floor)

        # Add floors
        mock_floor_class.return_value = mock_floor1
        building.add_floor(FloorType.LOBBY)
        mock_floor_class.return_value = mock_floor2
        building.add_floor(FloorType.OFFICE)

        # Test retrieval
        floor1 = building.get_floor_by_number(1)
        assert floor1 == mock_floor1

        floor2 = building.get_floor_by_number(2)
        assert floor2 == mock_floor2

        # Test non-existent floor
        floor_none = building.get_floor_by_number(99)
        assert floor_none is None


class TestBuildingElevatorOperations:
    """Test elevator-related operations"""


    def test_get_elevator_banks_on_floor(self, mock_logger_provider: MagicMock) -> None:
        """Test getting elevator banks that serve a specific floor"""
        building = Building(mock_logger_provider)

        # Create mock elevator banks with different floor ranges
        mock_bank1 = MagicMock(spec=ElevatorBank)
        mock_bank1.min_floor = 1
        mock_bank1.max_floor = 5

        mock_bank2 = MagicMock(spec=ElevatorBank)
        mock_bank2.min_floor = 3
        mock_bank2.max_floor = 8

        mock_bank3 = MagicMock(spec=ElevatorBank)
        mock_bank3.min_floor = 6
        mock_bank3.max_floor = 10

        # Bank without min/max_floor attributes
        mock_bank_no_attrs = MagicMock(spec=ElevatorBank)
        del mock_bank_no_attrs.min_floor
        del mock_bank_no_attrs.max_floor

        building.add_elevator_bank(mock_bank1)
        building.add_elevator_bank(mock_bank2)
        building.add_elevator_bank(mock_bank3)
        building.add_elevator_bank(mock_bank_no_attrs)

        # Test floor 4 - should get bank1 and bank2
        banks_on_4 = building.get_elevator_banks_on_floor(4)
        assert len(banks_on_4) == 2
        assert mock_bank1 in banks_on_4
        assert mock_bank2 in banks_on_4
        assert mock_bank3 not in banks_on_4
        assert mock_bank_no_attrs not in banks_on_4

        # Test floor 7 - should get bank2 and bank3
        banks_on_7 = building.get_elevator_banks_on_floor(7)
        assert len(banks_on_7) == 2
        assert mock_bank2 in banks_on_7
        assert mock_bank3 in banks_on_7
        assert mock_bank1 not in banks_on_7

        # Test floor outside all ranges
        banks_on_15 = building.get_elevator_banks_on_floor(15)
        assert len(banks_on_15) == 0


    def test_get_elevators(self, mock_logger_provider: MagicMock) -> None:
        """Test getting all elevators from all banks"""
        building = Building(mock_logger_provider)

        # Create mock elevators
        mock_elevator1 = MagicMock(spec=Elevator)
        mock_elevator2 = MagicMock(spec=Elevator)
        mock_elevator3 = MagicMock(spec=Elevator)

        # Create mock banks with elevators
        mock_bank1 = MagicMock(spec=ElevatorBank)
        mock_bank1.elevators = [mock_elevator1, mock_elevator2]

        mock_bank2 = MagicMock(spec=ElevatorBank)
        mock_bank2.elevators = [mock_elevator3]

        building.add_elevator_bank(mock_bank1)
        building.add_elevator_bank(mock_bank2)

        all_elevators = building.get_elevators()
        assert len(all_elevators) == 3
        assert mock_elevator1 in all_elevators
        assert mock_elevator2 in all_elevators
        assert mock_elevator3 in all_elevators


class TestBuildingUpdateAndDraw:
    """Test update and draw methods"""


    def test_update(self, mock_logger_provider: MagicMock) -> None:
        """Test update method (currently just passes)"""
        building = Building(mock_logger_provider)

        # Should not raise any exceptions
        building.update(Time(1.0))
        building.update(Time(0.5))
        building.update(Time(2.0))

    def test_draw(self, mock_logger_provider: MagicMock) -> None:
        """Test draw method (currently just passes)"""
        building = Building(mock_logger_provider)
        mock_surface = MagicMock()

        # Should not raise any exceptions
        building.draw(mock_surface)
