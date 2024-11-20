from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Callable, Dict, List, Tuple

from src.simulation.grid.location import Location
from src.simulation.people.person.memories import Memories
from src.logger import logger

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.people.person.person import Person


class Direction(Enum):
    LEFT = "l"
    RIGHT = "r"
    UP = "u"
    DOWN = "d"


class Vision:
    def __init__(self, person: Person, grid: Grid, visibility: int) -> None:
        self._person = person
        self._grid = grid
        self._visibility = visibility
        self._directions: List[Tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        logger.debug(f"Vision system initialized for {self._person} with visibility radius {self._visibility}.", self._person)

    def look_around(self) -> Memories:
        """Initiates the visibility check and returns updated memories."""
        logger.debug(f"{self._person} is looking around.")
        memories: Memories = Memories(self._grid)
        current_location = deepcopy(self._person.get_location())
        logger.debug(f"Starting vision search from {current_location}.")
        self._search(current_location, self._visibility, memories, set())
        logger.debug(f"Vision search complete for {self._person}. Memory updated.", self._person)
        return memories

    def _search(
        self,
        location: Location,
        visibility: int,
        memory: Memories,
        blocked: set[Location],
    ) -> None:
        if visibility <= 0:
            logger.debug(f"Visibility range exhausted at {location}.")
            return
        if location in blocked:
            logger.debug(f"Location {location} is already blocked. Skipping.")
            return

        blocked.add(location)
        logger.debug(f"Searching location {location} with visibility {visibility}.")

        for dx, dy in self._directions:
            neighbor = Location(location.x + dx, location.y + dy)
            if self._grid.is_in_bounds(neighbor):
                if neighbor not in blocked:
                    self._process_location(memory, blocked, neighbor)
                    self._search(neighbor, visibility - 1, memory, blocked)
            else:
                logger.debug(f"Neighbor {neighbor} is out of bounds. Skipping.")

    def _process_location(self, memory: Memories, blocked: set[Location], location: Location) -> None:
        """Processes a location and updates memory if an object is found."""
        logger.debug(f"Processing location {location}.")

        non_blocking_objects: Dict[str, Callable[[Location], bool]] = {
            "empties": self._grid.is_empty,
            "construction_barn": self._grid.is_construction_barn,
            "construction_home": self._grid.is_construction_home,
            "farm": self._grid.is_farm,
            "construction_farm": self._grid.is_construction_farm,
            "construction_mine": self._grid.is_construction_mine,
            "tree": self._grid.is_tree,
        }
        for obj_type, check_fn in non_blocking_objects.items():
            if check_fn(location):
                logger.debug(f"{obj_type.capitalize()} found at {location}.")
                memory.add(f"{obj_type}s", location)
                return

        if self._is_blocking_object(location, memory):
            logger.debug(f"Blocking object found at {location}. View will be obstructed.")
            self._block_view(blocked, location)
            return

        logger.error(f"Unknown character detected at {location}. Raising exception.")
        raise Exception(f"Unknown character at: {location}")

    def _is_blocking_object(self, location: Location, memory: Memories) -> bool:
        """Checks if the location contains a blocking object."""
        blocking_objects: Dict[str, Callable[[Location], bool]] = {
            "barn": self._grid.is_barn,
            "home": self._grid.is_home,
            "mine": self._grid.is_mine,
        }

        for obj_type, check_fn in blocking_objects.items():
            if check_fn(location):
                logger.debug(f"Blocking object {obj_type.capitalize()} detected at {location}.")
                memory.add(f"{obj_type}s", location)
                return True
        return False

    def _block_view(self, blocked: set[Location], location: Location) -> None:
        """Marks the view as blocked for the given location."""
        logger.debug(f"Blocking view from {location}.")
        blocked.add(location)
        for direction in Direction:
            self._mark_blocked_in_direction(blocked, location, direction)

    def _mark_blocked_in_direction(self, blocked: set[Location], location: Location, direction: Direction) -> None:
        """Blocks visibility in a specific direction from the given location."""
        logger.debug(f"Blocking view from location {location} towards {direction.name}.")
        x, y = location.x, location.y
        if direction == Direction.LEFT:
            for k in range(x, -1, -1):
                blocked.add(Location(k, y))
                logger.debug(f"Location {Location(k, y)} blocked.")
        elif direction == Direction.RIGHT:
            for k in range(x, self._grid.get_width()):
                blocked.add(Location(k, y))
                logger.debug(f"Location {Location(k, y)} blocked.")
        elif direction == Direction.DOWN:
            for k in range(y, self._grid.get_height()):
                blocked.add(Location(x, k))
                logger.debug(f"Location {Location(x, k)} blocked.")
        elif direction == Direction.UP:
            for k in range(y, -1, -1):
                blocked.add(Location(x, k))
                logger.debug(f"Location {Location(x, k)} blocked.")
