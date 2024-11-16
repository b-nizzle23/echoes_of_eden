from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, override, Optional

from src.simulation.people.person.scheduler.task.task import Task

if TYPE_CHECKING:
    from src.simulation.simulation import Simulation
    from src.simulation.people.person.person import Person
    from src.simulation.people.person.movement.move_result import MoveResult
    from src.simulation.grid.structure.work.construction.construction import Construction
    from src.simulation.grid.structure.structure_type import StructureType
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.grid.structure.store.store import Store


class Build(Task, ABC):
    def __init__(
        self,
        simulation: Simulation,
        person: Person,
        priority: int,
        build_structure: StructureType,
        store_structure: StructureType,
    ) -> None:
        super().__init__(simulation, person, priority)
        self._build_structure: StructureType = build_structure
        self._store_structure: StructureType = store_structure

        self._what_resource: Optional[str] = None
        self._resource: Optional[int] = None
        self._build: Optional[Construction] = None
        self._store: Optional[Store] = None

    @override
    def execute(self) -> None:
        if self._build:
            if self._build.needs_stone():
                self._what_resource = "stone"
            elif self._build.needs_wood():
                self._what_resource = "wood"
            elif self._what_resource:
                if self._store:
                    if self._what_resource == "stone":
                        self._build.deliver_stone(
                            self._store.remove_resource(
                                self._what_resource, self._build.how_much_stone()
                            )
                        )
                    else:
                        self._build.deliver_wood(
                            self._store.remove_resource(
                                self._what_resource, self._build.how_much_wood()
                            )
                        )
                    self._finished()
                else:
                    move_result: MoveResult = (
                        self._person.move_to_workable_structure(self._store_structure, self._what_resource)
                    )
                    if move_result.has_failed():
                        self._finished(False)
                        return 
                    self._store: Optional[Store] = move_result.get_structure()
            else:
                if self._build.work(self._person):
                    self._finished()
        else:
            move_result: MoveResult = (
                self._person.move_to_workable_structure(self._build_structure)
            )
            if move_result.has_failed():
                self._finished(False)
                return 
            self._build: Optional[Construction] = move_result.get_structure()

    @override
    def _clean_up_task(self) -> None:
        if self._build:
            self._build.remove_worker(self._person)

    @override
    def get_remaining_time(self) -> int:
        return (
            self._person.move_to_time_estimate() + self._build.work_time_estimate()
            if self._build
            else 3
        )

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return self._build
