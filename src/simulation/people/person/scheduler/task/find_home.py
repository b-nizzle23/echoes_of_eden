from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.structure import Structure
from task import Task
from typing import override, Optional

from src.simulation.people.person.person import Person
from src.simulation.simulation import Simulation


class FindHome(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation, person, 5)

    @override
    def execute(self) -> None:
        if not self._person.has_home():
            all_home_locations = self._simulation.get_grid().get_home_locations()
            # query the grid to make sure there is a home in that location
            for home_location in self._person.get_home_locations():
                if home_location in all_home_locations:
                    structure: Structure = self._simulation.get_grid().get_structure(
                        home_location
                    )
                    if isinstance(structure, Home):
                        if not structure.has_owner():
                            structure.assign_owner(self._person)
                            self._person.assign_home(structure)
                            self._finished()
                            return
                    else:
                        raise Exception(
                            "You are trying to go to a Home but are getting a different Structure"
                        )
            # if all homes have owners, construction a home (add build_home task)
            self._person.start_home_construction()
        else:
            self._finished()

    @override
    def _clean_up_task(self) -> None:
        pass

    @override
    def get_remaining_time(self) -> int:
        return 0

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return None
