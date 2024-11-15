from typing import Optional

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.store.store import Store
from src.simulation.people.person.person import Person


class Home(Store):
    def __init__(self, grid: Grid, location: Location) -> None:
        # Home only stores food, with a maximum of 36
        allowed_resources = {"food": 36}  # Only food can be stored
        super().__init__(grid, location, 2, 2, "H", allowed_resources)
        self._owner: Optional[Person] = None

    def has_owner(self) -> bool:
        return self._owner is not None

    def assign_owner(self, person: Person) -> None:
        self._owner = person

    def remove_owner(self) -> None:
        self._owner.remove_home()
