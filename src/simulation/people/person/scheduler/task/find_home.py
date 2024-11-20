from __future__ import annotations

from typing import TYPE_CHECKING, Optional, override

from src.settings import settings
from src.simulation.grid.structure.store.home import Home
from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.simulation.grid.structure.structure_factory import logger

if TYPE_CHECKING:
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class FindHome(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation, person, settings.get("find_home_priority", 5), TaskType.FIND_HOME)

    @override
    def execute(self) -> None:
        if not self._person.has_home():
            all_home_locations = self._simulation.get_grid().get_structure_locations(Home)
            # query the grid to make sure there is a home in that location
            home_locations = self._person.get_memories().get_home_locations()
            for home_location in home_locations:
                if home_location in all_home_locations:  # if the house still exists
                    structure: Structure = self._simulation.get_grid().get_structure(home_location)
                    if isinstance(structure, Home):
                        if not structure.has_owner():
                            structure.assign_owner(self._person)
                            self._person.assign_home(structure)
                            self._finished()
                            logger.info(f"{self._person} found a home")
                            return
                    else:
                        raise Exception("You are trying to go to a Home but are getting a different Structure")
            # if all homes have owners, construction a home (add build_home task)
            logger.info(f"{self._person} needs to start building a home")
            self._person.start_home_construction()
        else:
            self._finished()
            logger.warning(f"{self._person} should already has a home: {self._person.has_home()}")

    @override
    def _clean_up_task(self) -> None:
        pass

    @override
    def get_remaining_time(self) -> int:
        return 0

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return None
