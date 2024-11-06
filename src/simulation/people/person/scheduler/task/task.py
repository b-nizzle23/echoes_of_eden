from abc import ABC, abstractmethod

from src.simulation.grid.grid import Grid
from src.simulation.people.person.person import Person


class Task(ABC):
    def __init__(self, grid: Grid, person: Person, priority: int) -> None:
        self._grid: Grid = grid
        self._person: Person = person
        self._priority: int = priority  # 10 high to 1 low
        self._is_finished: bool = False

    def __lt__(self, other: "Task") -> bool:
        return self.get_priority() < other.get_priority()

    def get_priority(self) -> int:
        return self._priority

    def _finished(self) -> None:
        self._is_finished = True

    def is_finished(self) -> bool:
        return self._is_finished

    @abstractmethod
    def execute(self) -> None:
        # move to the task
        # do the task
        pass
