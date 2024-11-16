from __future__ import annotations

from typing import TYPE_CHECKING, override, Optional

from src.settings import settings
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.scheduler.task.task_type import TaskType

from src.simulation.people.person.scheduler.task.task import Task

if TYPE_CHECKING:
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation
    from src.simulation.people.person.movement.move_result import MoveResult
    from src.simulation.grid.structure.store.barn import Barn
    from src.simulation.grid.structure.store.home import Home
    from src.simulation.grid.structure.structure import Structure


class Eat(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation,
                         person,
                         settings.get("eat_priority", 5),
                         TaskType.EAT)

        self._home: Optional[Home] = None
        self._barn: Optional[Barn] = None
        self._food: int = 0

    @override
    def execute(self) -> None:
        if self._person.is_satiated():
            self._finished()
            return

        if self._person.has_home():
            self._handle_home_food_logic()
        else:
            self._handle_barn_food_logic()

    def _handle_home_food_logic(self) -> None:
        self._home = self._person.move_to_home()

        if self._home:
            if self._food:
                self._deposit_food_at_home()
            elif not self._home.has_capacity():
                self._eat_at_home()
            else:
                self._acquire_food_from_barn()

    def _deposit_food_at_home(self) -> None:
        self._person.move_to_home()
        self._home.add_resource(settings.get("food", "food"),
                                self._food)
        self._food = 0

    def _eat_at_home(self) -> None:
        self._person.eat(self._home)
        self._finished()

    def _acquire_food_from_barn(self) -> None:
        if not self._barn:
            move_result: MoveResult = self._person.move_to_workable_structure(StructureType.BARN,
                                                                              settings.get("food", "food"))
            if move_result.has_failed():
                self._finished(False)
                return 
            self._barn = move_result.get_structure()

        if self._barn:
            self._food = self._barn.remove_resource(settings.get("food", "food"),
                                                    self._home.get_capacity())
            # if the barn has no food, start working a farm to get food
            if self._food <= 0:
                self._person.work_farm()

    def _handle_barn_food_logic(self) -> None:
        if not self._barn:
            move_result: MoveResult = self._person.move_to_workable_structure(
                StructureType.BARN, settings.get("food", "food")
            )
            if move_result.has_failed():
                self._finished(False)
                return 
            self._barn = move_result.get_structure()

        if self._barn:
            # if the barn is out of food, go work the farm to get some food
            if self._barn.get_resource(settings.get("food", "food")) <= 0:
                self._person.work_farm()
            else:
                self._person.eat(self._barn)
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
