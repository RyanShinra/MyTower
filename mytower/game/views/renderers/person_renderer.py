from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING #, Dict, List
from pygame import Surface

if TYPE_CHECKING:
    from mytower.game.models.model_snapshots import PersonSnapshot
    from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class PersonRenderer:
    def __init__(self, logger_provider: LoggerProvider) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("PersonRenderer")

    def draw(self, surface: Surface, person: PersonSnapshot) -> None:
        self._logger.debug(f"Drawing person: {person.person_id}")
        # Draw the person on the given surface

