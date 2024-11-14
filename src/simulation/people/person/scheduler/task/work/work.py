from abc import ABC
from typing import override

from typing_extensions import Optional

from src.simulation.grid.location import Location
from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.structure.work.work import Work as WorkStructure
from src.simulation.people.person.movement.move_result import MoveResult
from src.simulation.people.person.person import Person
from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.simulation import Simulation


class Work(Task, ABC):
    def __init__(
        self,
        simulation: Simulation,
        person: Person,
        priority: int,
        work_structure: StructureType,
        resource_name: str,
    ) -> None:
        super().__init__(simulation, person, priority)
        self._work_structure: StructureType = work_structure
        self._resource_name: str = resource_name

        self._work: Optional[WorkStructure] = None
        self._distance_cost: Optional[float] = None
        self._resource: Optional[float] = None
        self._structure_location: Optional[Location] = None

    @override
    def execute(self) -> None:
        if self._work:
            resource: Optional[int] = self._work.work(self._person)
            self._resource = resource
            if resource:
                self._person.get_backpack().add_resource(self._resource_name, resource)
                self._finished()
        else:
            location = self._person.decide_which_location(self._work_structure)
            self._structure_location = location
            self._distance_cost = self._person.move_to_location_estimate(self._structure_location)
            move_result: MoveResult = (
                self._person.move_to_decided_location(location, self._work_structure)
            )
            if move_result.has_failed():
                self._finished()
                return
            self._work: Optional[WorkStructure] = move_result.get_structure()
        reward = self._resource - (self._distance_cost * 4)
        self._person.update_memory_rewards(self._structure_location, self._work_structure, reward)

    @override
    def _clean_up_task(self) -> None:
        if self._work:
            self._work.remove_worker(self._person)

    @override
    def get_remaining_time(self) -> int:
        return (
            self._person.move_to_time_estimate() + self._work.work_time_estimate()
            if self._work
            else 3
        )

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return self._work
