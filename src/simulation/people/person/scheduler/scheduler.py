import heapq
from typing import Optional, List

from src.simulation.people.person.person import Person
from src.simulation.people.person.scheduler.task.task_factory import TaskFactory
from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.simulation.simulation import Simulation


class Scheduler:
    def __init__(self, simulation: Simulation, person: Person) -> None:
        # TODO: maybe change how tasks are being stored?
        self._task_factory: TaskFactory = TaskFactory(simulation, person)
        self._tasks: List[Task] = []
        self._current_task: Optional[Task] = None

    def add(self, what: TaskType) -> None:
        task: Task = self._task_factory.create_instance(what)
        heapq.heappush(self._tasks, task)

    def _add(self, task: Task | None) -> None:
        if not Task:
            return 
        heapq.heappush(self._tasks, task)
        
    def _pop(self) -> Task | None:
        return heapq.heappop(self._tasks)

    def execute(self) -> None:
        if not self._current_task and not self._tasks:
            return
        if not self._current_task and self._tasks:
            self._current_task = self._pop()

        self._add(self._current_task)
        next_task: Task | None = self._pop()

        if self._current_task != next_task:
            self._current_task = next_task

        self._current_task.execute()
        if self._current_task.is_finished():
            self._current_task = None
