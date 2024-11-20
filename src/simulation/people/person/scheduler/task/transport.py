from __future__ import annotations

from typing import TYPE_CHECKING, Optional, override

from src.settings import settings
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.scheduler.task.task import Task

if TYPE_CHECKING:
    from src.simulation.grid.structure.store.store import Store
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.people.person.backpack import Backpack
    from src.simulation.people.person.movement.move_result import MoveResult
    from src.simulation.people.person.person import Person
    from src.simulation.people.person.scheduler.task.task_type import TaskType
    from src.simulation.simulation import Simulation


class Transport(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation, person, settings.get("transport_priority", 5), TaskType.TRANSPORT)
        self._backpack: Backpack = self._person.get_backpack()

        self._store_structure: StructureType = StructureType.BARN

        self._what_resource: Optional[str] = None
        self._resource: Optional[int] = None
        self._store: Optional[Store] = None

    @override
    def execute(self) -> None:
        if not self._backpack.has_items():
            self._finished(False)
            logger.warning("No items in backpack to transport")
            return
        if self._resource:  # resource is in hand. heading toward barn/home
            self._what_resource = self._backpack.what_resource()
            amount = self._backpack.get_resource(self._what_resource)
            self._resource = self._backpack.remove_resource(self._what_resource, amount)
            logger.debug(f"Removed {amount} {self._what_resource} from backpack")
        if self._store:  # I am at the store
            logger.debug(f"{self._person} should be at {self._store}")
            self._store.add_resource(self._what_resource, self._resource)
            self._what_resource = None
            self._resource = None
            self._store = None
            self._finished()
            logger.info(f"{self._person} added {self._resource} {self._what_resource} at {self._resource}")
        else:
            logger.debug(f"Need to go to workable structure, {self._store_structure}")
            move_result: MoveResult = self._person.move_to_workable_structure(self._store_structure)
            if move_result.has_failed():
                self._finished(False)
                logger.warning("Move result failed")
                return
            self._store: Optional[Store] = move_result.get_structure()
            logger.debug(f"Store {self._store} assigned to transport")

    @override
    def _clean_up_task(self) -> None:
        if self._what_resource and self._resource:
            self._backpack.add_resource(self._what_resource, self._resource)
            self._what_resource = None
            self._resource = None
            self._store = None

    @override
    def get_remaining_time(self) -> int:
        return 3

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return self._store
