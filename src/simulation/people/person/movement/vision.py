from copy import copy
from enum import Enum
from typing import Callable, Dict

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.people.person.memories import Memories
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

    def look_around(self) -> Memories:
        memory = Memories(self._person)
        current_location = copy(self._person.get_location())
        self._search(current_location, self._visibility, memory, set())
        return memory

    def _search(
        self,
        location: Location,
        visibility: int,
        memory: Memories,
        blocked: set[Location],
    ) -> None:
        if visibility <= 0 or location in blocked:
            return

        blocked.add(location)

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (dx, dy) == (0, 0):
                    continue
                next_loc = Location(location.x + dx, location.y + dy)
                if self._is_valid_location(next_loc, blocked):
                    self._process_location(memory, blocked, next_loc)
                    self._search(next_loc, visibility - 1, memory, blocked)

    def _process_location(
        self, memory: Memories, blocked: set[Location], location: Location
    ) -> None:
        if not self._grid.is_location_in_bounds(
            location
        ) or not self._grid.is_valid_location_for_person(location):
            return

        if self._is_blocking_object(location, memory):
            self._block_view(blocked, location)
        elif self._grid.is_empty(location):
            memory.add("empties", location)
        else:
            raise Exception(f"Unknown character at: {location}")

    def _is_blocking_object(self, location: Location, memory: Memories) -> bool:
        blocking_objects: Dict[str, Callable[[Location], bool]] = {
            "barn": self._grid.is_barn,
            "construction_barn": self._grid.is_construction_barn,
            "home": self._grid.is_home,
            "construction_home": self._grid.is_construction_home,
            "farm": self._grid.is_farm,
            "construction_farm": self._grid.is_construction_farm,
            "mine": self._grid.is_mine,
            "construction_mine": self._grid.is_construction_mine,
            "tree": self._grid.is_tree,
        }

        for obj_type, check_fn in blocking_objects.items():
            if check_fn(location):
                memory.add(f"{obj_type}s", location)
                return True
        return False

    def _block_view(self, blocked: set[Location], location: Location) -> None:
        blocked.add(location)
        for direction in Direction:
            self._mark_blocked_in_direction(blocked, location, direction)

    def _mark_blocked_in_direction(
        self, blocked: set[Location], location: Location, direction: Direction
    ) -> None:
        x, y = location.x, location.y
        if direction == Direction.LEFT:
            for k in range(x, -1, -1):
                blocked.add(Location(k, y))
        elif direction == Direction.RIGHT:
            for k in range(x, self._grid.get_width()):
                blocked.add(Location(k, y))
        elif direction == Direction.DOWN:
            for k in range(y, self._grid.get_height()):
                blocked.add(Location(x, k))
        elif direction == Direction.UP:
            for k in range(y, -1, -1):
                blocked.add(Location(x, k))

    def _is_valid_location(self, location: Location, blocked: set[Location]) -> bool:
        return not self._is_out_of_bounds(location) and location not in blocked

    def _is_out_of_bounds(self, location: Location) -> bool:
        return (
            location.x < 0
            or location.y < 0
            or location.x >= self._grid.get_width()
            or location.y >= self._grid.get_height()
        )
