from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import Future

from mytower.game.core.id_generator import IDGenerator


class TestIDGeneratorBasics:
    """Test basic IDGenerator functionality"""

    def test_initial_state(self) -> None:
        """Test that IDGenerator initializes with correct values"""
        generator = IDGenerator("test", radix=1, first_id=1)

        first_id: str = generator.get_next_id()
        assert first_id == "test_1"

        second_id: str = generator.get_next_id()
        assert second_id == "test_2"

    def test_custom_prefix(self) -> None:
        """Test IDGenerator with custom prefix"""
        generator = IDGenerator("person", radix=1, first_id=100)

        first_id: str = generator.get_next_id()
        assert first_id == "person_100"

        second_id: str = generator.get_next_id()
        assert second_id == "person_101"

    def test_custom_radix(self) -> None:
        """Test IDGenerator with custom radix"""
        generator = IDGenerator("elevator", radix=5, first_id=10)

        first_id = generator.get_next_id()
        assert first_id == "elevator_10"

        second_id = generator.get_next_id()
        assert second_id == "elevator_15"

        third_id = generator.get_next_id()
        assert third_id == "elevator_20"

    def test_reset_functionality(self) -> None:
        """Test that reset resets the counter"""
        generator = IDGenerator("test", radix=1, first_id=1)

        # Generate a few IDs
        generator.get_next_id()
        generator.get_next_id()
        generator.get_next_id()

        # Reset to different starting point
        generator.reset(50)

        next_id = generator.get_next_id()
        assert next_id == "test_50"

    def test_thread_safety(self) -> None:
        """Test that IDGenerator is thread-safe"""
        generator = IDGenerator("thread_test", radix=1, first_id=1)
        generated_ids: list[str] = []

        def generate_ids() -> None:
            for _ in range(100):
                generated_ids.append(generator.get_next_id())

        # Run multiple threads concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures: list[Future[None]] = [executor.submit(generate_ids) for _ in range(5)]
            for future in futures:
                future.result()

        # All IDs should be unique
        assert len(generated_ids) == 500
        assert len(set(generated_ids)) == 500

        # All IDs should follow expected pattern
        for id_str in generated_ids:
            assert id_str.startswith("thread_test_")
            assert id_str.split("_")[2].isdigit()

    def test_reset_thread_safety(self) -> None:
        """Test that reset is thread-safe"""
        generator = IDGenerator("reset_test", radix=1, first_id=1)

        def reset_and_generate():
            generator.reset(1)
            return generator.get_next_id()

        # Run multiple resets concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(reset_and_generate) for _ in range(3)]
            results = [future.result() for future in futures]

        # All results should be valid IDs
        for result in results:
            assert result.startswith("reset_test_")
            assert result.split("_")[2].isdigit()
