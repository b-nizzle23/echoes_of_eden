import heapq
from typing import List, Optional

from src.simulation.people.person.person import Person
from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.people.person.scheduler.task.task_factory import TaskFactory
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.simulation.simulation import Simulation


class Scheduler:
    def __init__(self, simulation: Simulation, person: Person) -> None:
        self._task_factory: TaskFactory = TaskFactory(simulation, person)
        self._all_tasks: List[Task] = []
        self._tasks: List[Task] = []
        self._current_task: Optional[Task] = None
        self._last_added_time = 0  # Timestamp for when the last task was added
        self._interruption_threshold = 3  # Initial threshold for interruptions
        self._max_interruption_threshold = 10  # Maximum interruption threshold
        self._simulation = (
            simulation  # Store the simulation reference to access the time
        )

    def get_all_tasks(self):
        return self._all_tasks

    def get_tasks(self):
        return self._tasks

    def flush(self):
        self._all_tasks = []

    def add(self, what: TaskType) -> None:
        unique: bool = True
        task: Task = self._task_factory.create_instance(what)
        if task:
            for other in self._tasks:
                if type(other) == type(task):
                    unique = False
                    break
            if unique:
                self._all_tasks.append(task)
                heapq.heappush(self._tasks, task)
                self._last_added_time = self._get_time()

    def _add(self, task: Optional[Task]) -> None:
        if task:
            heapq.heappush(self._tasks, task)

    def _pop(self) -> Optional[Task]:
        return heapq.heappop(self._tasks) if self._tasks else None

    def _get_time(self) -> int:
        return self._simulation.get_time()

    def _calculate_dynamic_threshold(self) -> int:
        # Calculate dynamic interruption threshold based on the current state
        base_threshold = max(1, len(self._tasks) // 2)

        task_addition_rate_factor = (
            1 if self._get_time() - self._last_added_time > 1 else 2
        )

        if self._current_task:
            priority_factor = (
                11 - self._current_task.get_priority()
            )  # Inverse relation: high priority = low threshold
        else:
            priority_factor = (
                6  # Default to mid-range priority factor if no current task
            )

        dynamic_threshold = min(
            self._max_interruption_threshold,
            base_threshold * task_addition_rate_factor * priority_factor,
        )

        return dynamic_threshold

    @staticmethod
    def _calculate_task_reward(task: Task) -> float:
        # Reward function: Higher priority tasks have higher rewards
        priority_weight = 11 - task.get_priority()  # Higher priority = higher weight
        time_remaining_weight = max(
            1, 10 - task.get_remaining_time()
        )  # Closer to completion = higher weight
        interruption_penalty = max(
            0, task.get_interruptions()
        )  # More interruptions = lower reward

        # Reward formula: Higher priority, less time remaining, fewer interruptions lead to higher reward
        reward = priority_weight * time_remaining_weight / (1 + interruption_penalty)
        return reward

    def execute(self) -> None:
        if not self._current_task and not self._tasks:
            return

        if not self._current_task and self._tasks:
            self._current_task = self._pop()

        # Calculate the dynamic interruption threshold based on the current state
        self._interruption_threshold = self._calculate_dynamic_threshold()

        # Calculate the reward for continuing the current task
        current_task_reward = self._calculate_task_reward(self._current_task)

        # Evaluate the reward of switching to the next task
        self._add(self._current_task)
        next_task: Optional[Task] = self._pop()
        next_task_reward = self._calculate_task_reward(next_task)

        # Apply the optimal stopping rule: stick to the current task if it has a higher reward
        if current_task_reward >= next_task_reward:
            self._current_task.execute()
            if self._current_task.is_finished():
                self._current_task = None
            return
        else:
            # If the next task has a higher reward, switch to it
            self._current_task.increment_interruptions()
            self._current_task = next_task

        self._current_task.execute()

        if self._current_task.is_finished():
            self._current_task = None
