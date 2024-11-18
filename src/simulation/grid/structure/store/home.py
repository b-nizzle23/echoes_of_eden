from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from src.simulation.grid.structure.store.store import Store
from src.settings import settings
from src.logger import logger

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location
    from src.simulation.people.person.person import Person


class Home(Store):
    def __init__(self, grid: Grid, location: Location) -> None:
        logger.debug(f"Initializing Home at location {location}")

        allowed_resources = {"food": settings.get("home_food_store", 36)}  # Only food can be stored

        logger.debug(f"Allowed resources for the Home: {allowed_resources}")

        super().__init__(grid, location,
                         settings.get("home_size", 2),
                         settings.get("home_size", 2),
                         settings.get("home_char", "H"),
                         allowed_resources)

        self._owner: Optional[Person] = None
        logger.info(f"Home initialized at location {location}.")

    def has_owner(self) -> bool:
        logger.debug(f"Checking if Home has an owner.")
        return self._owner is not None

    def assign_owner(self, person: Person) -> None:
        logger.info(f"Assigning owner {person} to the Home.")
        self._owner = person

    def remove_owner(self) -> None:
        logger.info(f"Removing owner from the Home.")
        if self._owner:
            self._owner.remove_home()
        self._owner = None
