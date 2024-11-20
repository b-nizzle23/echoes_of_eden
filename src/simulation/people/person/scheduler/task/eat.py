from __future__ import annotations

from typing import TYPE_CHECKING, Optional, override

from src.settings import settings
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.people.person.scheduler.task.task_type import TaskType

if TYPE_CHECKING:
    from src.simulation.grid.structure.store.barn import Barn
    from src.simulation.grid.structure.store.home import Home
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.people.person.movement.move_result import MoveResult
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class Eat(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation, person, settings.get("eat_priority", 5), TaskType.EAT)

        self._home: Optional[Home] = None
        self._barn: Optional[Barn] = None
        self._food: int = 0

    @override
    def execute(self) -> None:
        if self._person.is_satiated():
            self._finished()
            logger.info(f"{self._person} is satiated")
            return

        if self._person.has_home():
            logger.debug(f"{self._person} is going to eat at home")
            self._handle_home_food_logic()
        else:
            logger.debug(f"{self._person} is going to eat at barn")
            self._handle_barn_food_logic()

    def _handle_home_food_logic(self) -> None:
        self._home = self._person.move_to_home()

        if self._home:
            if self._food:
                logger.debug(f"{self._person} is going to deposit food")
                self._deposit_food_at_home()
            elif not self._home.has_capacity():
                logger.debug(f"{self._person} is going to eat")
                self._eat_at_home()
            else:
                logger.debug(f"{self._person} is going to get food from barn")
                self._acquire_food_from_barn()

    def _deposit_food_at_home(self) -> None:
        self._person.move_to_home()
        self._home.add_resource(settings.get("food", "food"), self._food)
        self._food = 0

    def _eat_at_home(self) -> None:
        self._person.eat(self._home)
        self._finished()
        logger.info(f"{self._person} has eaten at home")

    def _acquire_food_from_barn(self) -> None:
        if not self._barn:
            logger.debug(f"{self._person} is going to a barn")
            move_result: MoveResult = self._person.move_to_workable_structure(
                StructureType.BARN, settings.get("food", "food")
            )
            if move_result.has_failed():
                self._finished(False)
                logger.warning("Move result failed")
                return
            self._barn = move_result.get_structure()
            logger.debug(f"{self._person} is at barn")

        if self._barn:
            self._food = self._barn.remove_resource(settings.get("food", "food"), self._home.get_capacity())
            logger.debug(f"{self._person} took {self._food} food from barn")
            # if the barn has no food, start working a farm to get food
            if self._food <= 0:
                self._person.work_farm()
                logger.info(f"{self._person} could not get food from barn. Needs to work farm")

    def _handle_barn_food_logic(self) -> None:
        if not self._barn:
            logger.debug(f"{self._person} is going to a barn")
            move_result: MoveResult = self._person.move_to_workable_structure(
                StructureType.BARN, settings.get("food", "food")
            )
            if move_result.has_failed():
                self._finished(False)
                logger.warning("Move result failed")
                return
            self._barn = move_result.get_structure()
            logger.debug(f"{self._person} is at barn")

        if self._barn:
            # if the barn is out of food, go work the farm to get some food
            if self._barn.get_resource(settings.get("food", "food")) <= 0:
                logger.info(f"{self._person} could not get food from barn. Needs to work farm")
                self._person.work_farm()
            else:
                self._person.eat(self._barn)
                logger.info(f"{self._person} has eaten at barn")
                self._finished()

    @override
    def _clean_up_task(self) -> None:
        self._home = None
        self._barn = None
        self._food = 0

    @override
    def get_remaining_time(self) -> int:
        return self._person.move_to_time_estimate() + 1

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return None
