from __future__ import annotations

import heapq
from typing import TYPE_CHECKING, List, Optional

from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.person.scheduler.task.task_factory import \
    TaskFactory

if TYPE_CHECKING:
    from src.simulation.people.person.person import Person
    from src.simulation.people.person.scheduler.task.task import Task
    from src.simulation.people.person.scheduler.task.task_type import TaskType
    from src.simulation.simulation import Simulation


class Scheduler:
    _small_float = 2**-100

    def __init__(self, simulation: Simulation, person: Person) -> None:
        self._task_factory: TaskFactory = TaskFactory(simulation, person)
        self._this_years_tasks: List[Task] = []
        self._tasks: List[Task] = []
        self._current_task: Optional[Task] = None
        self._simulation = simulation

    def get_this_years_tasks(self):
        return self._this_years_tasks

    def get_tasks(self):
        return self._tasks

    def flush(self):
        self._this_years_tasks = []

    def add(self, what: TaskType) -> None:
        task: Task = self._task_factory.create_instance(what)
        if not task:
            logger.warning(f"Tried to add invalid task: {what}")
            return
        task_types = {type(task) for task in self._tasks}
        if type(task) not in task_types:
            self._add(task)
            self._this_years_tasks.append(task)
            logger.debug(f"Task {task} should be added to list of tasks")

    def _add(self, task: Optional[Task]) -> None:
        if task:
            heapq.heappush(self._tasks, task)

    def _pop(self) -> Optional[Task]:
        return heapq.heappop(self._tasks) if self._tasks else None

    def _calculate_task_reward(self, task: Task) -> float:
        if not task:
            return self._small_float
        # Reward function: Higher priority tasks have higher rewards
        priority_weight = 11 - task.get_priority()  # Higher priority = higher weight
        time_remaining_weight = max(1, 10 - task.get_remaining_time())  # Closer to completion = higher weight
        interruption_penalty = max(0, task.get_interruptions())  # More interruptions = lower reward

        # Reward formula: Higher priority, less time remaining, fewer interruptions lead to higher reward
        reward = priority_weight * time_remaining_weight / (1 + interruption_penalty)
        logger.debug(f"Task {task} should have reward {reward}")
        return reward

    def execute(self) -> None:
        if not self._current_task and not self._tasks:
            logger.warning("Tried to execute task, no tasks to execute")
            return

        if not self._current_task and self._tasks:
            logger.debug(f"No current task, popping task from list of tasks")
            self._current_task = self._pop()

        # Calculate the reward for continuing the current task
        current_task_reward = self._calculate_task_reward(self._current_task)

        # Evaluate the reward of switching to the next task
        next_task: Optional[Task] = self._pop()
        next_task_reward: float = self._calculate_task_reward(next_task)

        # Apply the optimal stopping rule: stick to the current task if it has a higher reward
        if current_task_reward < next_task_reward:
            logger.info(f"Next task {next_task} has higher reward. Switching from {self._current_task} to {next_task}")
            self._current_task.increment_interruptions()
            self._add(self._current_task)
            self._current_task = next_task
        else:
            self._add(next_task)

        logger.debug(f"Should be executing {self._current_task}")
        self._current_task.execute()


        if self._current_task.is_finished():
            logger.debug(f"Current task {self._current_task} is finished")
            self._current_task = None
