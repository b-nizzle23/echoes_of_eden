import heapq

from simulation.people.person.scheduler.task.task_factory import TaskFactory


class Scheduler:
    def __init__(self, simulation, person):
        # TODO: maybe change how tasks is being stored?
        self._task_factory = TaskFactory(simulation, person)
        self._tasks = []
        self._current_task = None

    def add(self, what):
        task = self._task_factory.create_instance(what)
        heapq.heappush(self._tasks, task)

    def _add(self, task):
        heapq.heappush(self._tasks, task)

    def execute(self):
        if not self._current_task and not self._tasks:
            return
        if not self._current_task and self._tasks:
            self._current_task = heapq.heappop(self._tasks)

        self.add(self._current_task)
        next_task = heapq.heappop(self._tasks)

        if self._current_task != next_task:
            self._current_task = next_task

        self._current_task.execute()
        if self._current_task.is_finished():
            self._current_task = None
