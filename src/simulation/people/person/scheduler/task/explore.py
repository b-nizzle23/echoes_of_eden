from __future__ import annotations

from typing import TYPE_CHECKING, Optional, override

from src.settings import settings
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.people.person.scheduler.task.task_type import TaskType

if TYPE_CHECKING:
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class Explore(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation, person, settings.get("explore_priority", 5), TaskType.EXPLORE)
        self._max_how_far: int = 5
        self._how_far: int = 0

    @override
    def execute(self) -> None:
        self._how_far += 1
        self._person.explore()
        if self._how_far >= self._max_how_far:
            logger.info(f"{self._person} explored {self._max_how_far} times")
            self._finished()

    @override
    def _clean_up_task(self) -> None:
        pass

    @override
    def get_remaining_time(self) -> int:
        return 5

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return None
