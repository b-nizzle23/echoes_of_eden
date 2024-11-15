from abc import ABC, abstractmethod
from typing import Optional

from src.simulation.grid.structure.structure import Structure
from src.simulation.people.person.person import Person
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.simulation.simulation import Simulation


class Task(ABC):
    def __init__(self, simulation: Simulation, person: Person, priority: int, task_type: TaskType) -> None:
        self._simulation: Simulation = simulation
        self._person: Person = person
        self._priority: int = priority  # 10 high to 1 low
        self._is_finished: bool = False
        self._interruptions: int = 0
        self._is_completed: bool = False
        self._task_type: TaskType = task_type

    def __lt__(self, other: "Task") -> bool:
        return self.get_priority() < other.get_priority()

    def get_interruptions(self) -> int:
        return self._interruptions

    def increment_interruptions(self) -> None:
        self._interruptions += 1
        self._clean_up_task()

    def get_priority(self) -> int:
        return self._priority

    def _finished(self, is_completed: bool = True) -> None:
        self._is_completed = is_completed
        self._is_finished = True
        if self._task_type == TaskType.WORK_FARM or self._task_type == TaskType.WORK_MINE or self._task_type == TaskType.CHOP_TREE:
            if is_completed:
                reward = 1
            else:
                reward = -1
            self._person.update_scheduler_rewards(reward, self._task_type)

    def is_finished(self) -> bool:
        return self._is_finished

    @abstractmethod
    def execute(self) -> None:
        # move to the task
        # do the task
        pass

    @abstractmethod
    def get_remaining_time(self) -> int:
        # ballpark: how many action cycles will this task take?
        pass

    @abstractmethod
    def _clean_up_task(self) -> None:
        # stop the work you are doing
        pass

    @abstractmethod
    def get_work_structure(self) -> Optional[Structure]:
        # the structure the task works at or none if there is no structure for the task
        pass
