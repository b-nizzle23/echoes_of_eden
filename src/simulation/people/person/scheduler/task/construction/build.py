from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional, override

from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.logger import logger

if TYPE_CHECKING:
    from src.simulation.grid.structure.store.store import Store
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.grid.structure.structure_type import StructureType
    from src.simulation.grid.structure.work.construction.construction import \
        Construction
    from src.simulation.people.person.movement.move_result import MoveResult
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class Build(Task, ABC):
    def __init__(
        self,
        simulation: Simulation,
        person: Person,
        build_structure: StructureType,
        store_structure: StructureType,
        task_type: TaskType
    ) -> None:
        super().__init__(simulation, person, task_type)
        self._build_structure: StructureType = build_structure
        self._store_structure: StructureType = store_structure

        self._what_resource: Optional[str] = None
        self._resource: Optional[int] = None
        self._build: Optional[Construction] = None
        self._store: Optional[Store] = None

    @override
    def execute(self) -> None:
        if self._build and not (self._person.get_location().is_one_away(self._build.get_location())
                               or self._person.get_location().is_at_same_location(self._build.get_location())):

            self._person.go_to_location(self._build.get_location())

        if self._build and (self._person.get_location().is_one_away(self._build.get_location())
                           or self._person.get_location().is_at_same_location(self._build.get_location())):
            if self._build.needs_stone():
                self._what_resource = "stone"
                logger.debug(f"Needs stone to build")
            elif self._build.needs_wood():
                self._what_resource = "wood"
                logger.debug(f"Needs wood to build")
            elif self._what_resource:
                if self._store:
                    if self._what_resource == "stone":
                        logger.debug(f"Going to deliver stone to {self._build}")
                        self._build.deliver_stone(
                            self._store.remove_resource(self._what_resource, self._build.how_much_stone())
                        )
                    else:
                        logger.debug(f"Going to deliver wood to {self._build}")
                        self._build.deliver_wood(
                            self._store.remove_resource(self._what_resource, self._build.how_much_wood())
                        )
                    self._finished()
                    logger.info(f"{self._build} is finished being built.")
                else:
                    logger.debug(f"Not building, need to go to a store structure for {self._what_resource}")
                    move_result: MoveResult = self._person.move_to_workable_structure(
                        self._store_structure, self._what_resource
                    )
                    if move_result.has_failed():
                        self._finished(False)
                        logger.warning("Move result failed")
                        return
                    self._store: Optional[Store] = move_result.get_structure()
                    logger.debug(f"Store {self._store} assigned to building {self._build}")
            else:
                if self._build.work(self._person):
                    self._finished()
                    logger.info(f"{self._build} is finished being built.")

        else:
            logger.debug(f"Not building, need to go to different workable structure")
            move_result: MoveResult = self._person.move_to_workable_structure(self._build_structure)
            self._build: Optional[Construction] = move_result.get_structure()
            if move_result.has_failed():
                logger.warning("Move result failed")
                self._finished(False)
                return
            logger.debug(f"Building {self._build} assigned to build")

    @override
    def _clean_up_task(self) -> None:
        if self._build:
            self._build.remove_worker(self._person)
            logger.debug(f"Removed worker,{self._person}, from {self._build}")

    @override
    def get_remaining_time(self) -> int:
        return self._person.move_to_time_estimate() + self._build.work_time_estimate() if self._build else 3

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return self._build
