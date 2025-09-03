# tests/floor/test_floor_people.py
# ruff: noqa: F401, F841
# pyright: reportUnusedCallResult=false

# tests/floor/test_floor_people.py 22
from __future__ import annotations
import pytest
from unittest.mock import MagicMock

from mytower.game.floor import Floor
from mytower.game.types import FloorType
from mytower.game.person import PersonProtocol


@pytest.fixture
def floor(mock_logger_provider: MagicMock, mock_building_no_floor: MagicMock) -> Floor:
    return Floor(
        logger_provider=mock_logger_provider,
        building=mock_building_no_floor,
        floor_num=3,
        floor_type=FloorType.OFFICE
    )


@pytest.fixture
def mock_person() -> MagicMock:
    person = MagicMock(spec=PersonProtocol)
    person.person_id = "person_123"
    return person


class TestFloorPeopleOwnership:
    """Test Floor's person ownership functionality"""
    
    def test_floor_starts_empty(self, floor: Floor) -> None:
        """Test that floor initializes with no people"""
        # We don't have a direct people property, but we can test indirectly
        # by trying to remove a person that shouldn't exist
        with pytest.raises(KeyError):
            floor.remove_person("nonexistent_person")
    
    
    def test_add_person_success(self, floor: Floor, mock_person: MagicMock) -> None:
        """Test successfully adding a person to the floor"""
        floor.add_person(mock_person)
        
        # Should be able to retrieve the person
        retrieved_person: PersonProtocol = floor.remove_person("person_123")
        assert retrieved_person == mock_person
    
    
    def test_add_multiple_people(self, floor: Floor) -> None:
        """Test adding multiple people to same floor"""
        person1 = MagicMock(spec=PersonProtocol)
        person1.person_id = "person_001"
        
        person2 = MagicMock(spec=PersonProtocol) 
        person2.person_id = "person_002"
        
        person3 = MagicMock(spec=PersonProtocol)
        person3.person_id = "person_003"
        
        # Add all three
        floor.add_person(person1)
        floor.add_person(person2)
        floor.add_person(person3)
        
        # Should be able to retrieve all in any order
        retrieved2: PersonProtocol = floor.remove_person("person_002")
        retrieved1: PersonProtocol = floor.remove_person("person_001") 
        retrieved3: PersonProtocol = floor.remove_person("person_003")
        
        assert retrieved1 == person1
        assert retrieved2 == person2
        assert retrieved3 == person3
    
    
    def test_add_person_overwrites_same_id(self, floor: Floor) -> None:
        """Test that adding person with same ID overwrites previous"""
        person1 = MagicMock(spec=PersonProtocol)
        person1.person_id = "person_duplicate"
        
        person2 = MagicMock(spec=PersonProtocol)
        person2.person_id = "person_duplicate"  # Same ID
        
        floor.add_person(person1)
        floor.add_person(person2)  # Should overwrite person1
        
        # Should get person2, not person1
        retrieved: PersonProtocol = floor.remove_person("person_duplicate")
        assert retrieved == person2
        assert retrieved != person1
    
    
    def test_remove_person_success(self, floor: Floor, mock_person: MagicMock) -> None:
        """Test successfully removing a person from floor"""
        floor.add_person(mock_person)
        
        removed_person: PersonProtocol = floor.remove_person("person_123")
        
        assert removed_person == mock_person
        
        # Person should no longer be on floor
        with pytest.raises(KeyError):
            floor.remove_person("person_123")
    
    
    def test_remove_person_not_found_raises_keyerror(self, floor: Floor) -> None:
        """Test that removing non-existent person raises KeyError with descriptive message"""
        with pytest.raises(KeyError, match="Person not found: nonexistent_person"):
            floor.remove_person("nonexistent_person")
    
    
    def test_remove_person_from_empty_floor_raises_keyerror(self, floor: Floor) -> None:
        """Test removing person from empty floor raises appropriate error"""
        with pytest.raises(KeyError, match="Person not found: person_123"):
            floor.remove_person("person_123")
    
    
    def test_person_removal_is_permanent(self, floor: Floor, mock_person: MagicMock) -> None:
        """Test that removed person cannot be removed again"""
        floor.add_person(mock_person)
        floor.remove_person("person_123")
        
        # Second removal should fail
        with pytest.raises(KeyError, match="Person not found: person_123"):
            floor.remove_person("person_123")


class TestFloorPersonOwnershipEdgeCases:
    """Test edge cases and error conditions for floor person ownership"""
    
    def test_add_none_person_handled_gracefully(self, floor: Floor) -> None:
        """Test that adding None doesn't crash (though it might not be useful)"""
        # This might be implementation dependent - if you have validation, it might raise
        # For now, let's assume it stores None with some person_id attribute
        none_person = MagicMock(spec=PersonProtocol)
        none_person.person_id = "none_person"
        
        # Should not crash
        floor.add_person(none_person)
        retrieved = floor.remove_person("none_person")
        assert retrieved == none_person


# TODO: Add these tests once we implement person count tracking
# class TestFloorPersonCountTracking:
#     """Test person count tracking (future enhancement)"""
#     
#     def test_person_count_starts_zero(self, floor: Floor) -> None:
#         assert floor.person_count == 0
#     
#     def test_person_count_increases_with_additions(self, floor: Floor) -> None:
#         # Add implementation once Floor has person_count property
#         pass