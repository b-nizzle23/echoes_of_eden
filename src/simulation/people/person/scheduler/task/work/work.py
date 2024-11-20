from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, override

from typing_extensions import Optional

from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.person.scheduler.task.task import Task

if TYPE_CHECKING:
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.grid.structure.structure_type import StructureType
    from src.simulation.grid.structure.work.work import Work as WorkStructure
    from src.simulation.people.person.movement.move_result import MoveResult
    from src.simulation.people.person.person import Person
    from src.simulation.people.person.scheduler.task.task_type import TaskType
    from src.simulation.simulation import Simulation


class Work(Task, ABC):
    def __init__(
        self,
        simulation: Simulation,
        person: Person,
        priority: int,
        work_structure: StructureType,
        resource_name: str,
        task_type: TaskType,
    ) -> None:
        super().__init__(simulation, person, priority, task_type)
        self._work_structure: StructureType = work_structure
        self._resource_name: str = resource_name

        self._work: Optional[WorkStructure] = None

    @override
    def execute(self) -> None:
        if self._work:
            resource: Optional[int] = self._work.work(self._person)

            if resource:
                self._person.get_backpack().add_resource(self._resource_name, resource)
                self._person.update_navigator_rewards(resource)
                self._finished()
                logger.info(f"{self._person} got {resource} {self._resource_name}")
        else:
            move_result: MoveResult = self._person.move_to_workable_structure(self._work_structure)
            if move_result.has_failed():
                self._finished(False)
                logger.warning("Move result failed")
                return
            self._work: Optional[WorkStructure] = move_result.get_structure()
            logger.info(f"{self._person} is working at {self._work_structure}")

    @override
    def _clean_up_task(self) -> None:
        if self._work:
            self._work.remove_worker(self._person)
            logger.info(f"Removed worker,{self._person}, from {self._work_structure}")

    @override
    def get_remaining_time(self) -> int:
        return self._person.move_to_time_estimate() + self._work.work_time_estimate() if self._work else 3

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return self._work
