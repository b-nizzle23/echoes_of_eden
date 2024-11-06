from copy import copy
from random import randint
from typing import List, Optional

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as PathFindingGrid
from pathfinding.core.node import GridNode as PathFindingGridNode
from pathfinding.finder.dijkstra import DijkstraFinder

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
<<<<<<< Updated upstream:src/simulation/people/person/mover.py
from memory import Memory
from person import Person
from vision import Vision
=======
from src.simulation.people.person._memory import Memory
from src.simulation.people.person.person import Person
from src.simulation.people.person._vision import Vision
from typing import Optional, List
>>>>>>> Stashed changes:src/simulation/people/person/_mover.py


class Mover:
    def __init__(self, grid: Grid, person: Person, memory: Memory, speed: int) -> None:
        self._person = person
        self._grid = grid
        self._speed = speed
        self._memory = memory
        self._vision = Vision(person, grid, 30)

    def explore(self) -> None:
        random_location = self._get_random_location()
        self.towards(random_location)

    def towards(self, target: Location) -> None:
        if not self._grid.is_location_in_bounds(
            target
        ) or not self._grid.is_valid_location_for_person(target):
            return

        for _ in range(self._speed):
            current_location = copy(self._person.get_location())
            self._memory.combine(self._vision.look_around())
            path_finding_grid = self._get_path_finding_grid()
            path = self._get_path(current_location, path_finding_grid, target)

            if path and len(path) >= 2:
                next_node = path[1]
                new_location = Location(next_node.y, next_node.x)  # Convert to Location
                self._place(new_location)

    @staticmethod
    def get_closest(
        current_location: Location, locations: List[Location]
    ) -> Optional[Location]:
        if not locations:
            return None
        return min(
            locations, key=lambda loc: current_location.distance_to(loc), default=None
        )

    @staticmethod
    def get_furthest(
        current_location: Location, locations: List[Location]
    ) -> Optional[Location]:
        if not locations:
            return None
        return max(
            locations, key=lambda loc: current_location.distance_to(loc), default=None
        )

    def is_next_to(self, locations: List[Location]) -> bool:
        current_location = copy(self._person.get_location())
        return any(current_location.is_one_away(loc) for loc in locations)

    @staticmethod
    def is_near(location1: Location, location2: Location, distance: int = 5) -> bool:
        return location1.distance_to(location2) < distance

    def can_get_to_location(self, target: Location) -> bool:
        path_finding_grid = self._get_path_finding_grid()
        return bool(
            self._get_path(copy(self._person.get_location()), path_finding_grid, target)
        )

    def _place(self, location: Location) -> None:
        current_location = copy(self._person.get_location())
        if not current_location.is_one_away(location):
            raise ValueError(f"Location is not one away: {location}")
        if not self._grid.is_location_in_bounds(
            location
        ) or not self._grid.is_valid_location_for_person(location):
            raise ValueError(f"Location is not valid: {location}")
        self._person.set_location((location.x, location.y))

    def _get_random_location(self) -> Location:
        while True:
            x = randint(0, self._grid.get_width() - 1)
            y = randint(0, self._grid.get_height() - 1)
            location = Location(x, y)
            if self._grid.is_location_in_bounds(
                location
            ) and self._grid.is_valid_location_for_person(location):
                return location

    def _get_path(
        self,
        current_location: Location,
        path_finding_grid: PathFindingGrid,
        target: Location,
    ) -> List[PathFindingGridNode]:
        if not self._grid.is_location_in_bounds(
            current_location
        ) or not self._grid.is_valid_location_for_person(current_location):
            raise ValueError("Person out of bounds")

        start_node = path_finding_grid.node(current_location.y, current_location.x)
        end_node = path_finding_grid.node(target.y, target.x)

        finder = DijkstraFinder(diagonal_movement=DiagonalMovement.always)
        path, _ = finder.find_path(start_node, end_node, path_finding_grid)
        return path

    def _get_path_finding_grid(self) -> PathFindingGrid:
        matrix = self._grid.get_path_finding_matrix()
        return PathFindingGrid(matrix=matrix)
