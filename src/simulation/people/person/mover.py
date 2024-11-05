from random import randint
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as PathFindingGrid
from src.simulation.grid.grid import Grid

from pathfinding.finder.dijkstra import DijkstraFinder
from copy import deepcopy

from src.simulation.people.person.memory import Memory
from src.simulation.people.person.person import Person
from src.simulation.people.person.vision import Vision
from typing import Optional, List, Tuple, Any


class Mover:
    def __init__(self, grid: Grid, person: Person, memory: Memory, speed: int) -> None:
        self._person = person
        self._grid = grid
        self._speed = speed
        self._memory = memory
        self._vision = Vision(person, grid, 30)

    def explore(self) -> None:
        while True:
            random_location = self._get_random_location()
            return self.towards(random_location)

    def towards(self, location: Optional[Tuple[int, int]]) -> None:
        if location is None:
            return

        if not self._grid.is_location_in_bounds(location):
            return

        # TODO check if person gets stuck
        for _ in range(self._speed):
            location = self._person.get_location()
            self._memory.combine(self._vision.look_around())
            n_x = -1
            n_y = -1
            path_finding_grid = self._get_path_finding_grid()
            path = self._get_path(location, path_finding_grid)
            if path and len(path) >= 2:
                node = path[1]
                n_x = node.y
                n_y = node.x
            if n_x == -1 or n_y == -1:
                return

            new_location = (n_x, n_y)
            self._place(new_location)

    def _place(self, location: Tuple[int, int]) -> None:
        if not self._is_one_away(self._person.get_location(), location):
            raise Exception(f"location is not one away: {location}")
        if not self._grid.is_valid_location_for_person(location):
            raise Exception(f"location is not valid: {location}")
        self._person.set_location(location)

    def _get_random_location(self) -> Tuple[int, int]:
        while True:
            x = randint(0, self._grid.get_width() - 1)
            y = randint(0, self._grid.get_width() - 1)
            location = (x, y)
            if self._grid.is_valid_location_for_person(location):
                break
        return location

    def _get_path(self, location: Tuple[int, int], path_finding_grid: PathFindingGrid) -> List[Any]:
        if location is None:
            raise Exception("location is None")
        if path_finding_grid is None:
            raise Exception("path_finding_grid is None")
        if not self._grid.is_location_in_bounds(self._person.get_location()):
            raise Exception("Person out of bounds")
        x1, y1 = self._person.get_location()
        start = path_finding_grid.node(y1, x1)
        x2 = location[1]
        y2 = location[2]
        end = path_finding_grid.node(y2, x2)
        finder = DijkstraFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, path_finding_grid)
        return path

    def _get_path_finding_grid(self) -> PathFindingGrid:
        matrix: List[List[int]] = deepcopy(self._grid.get_path_finding_matrix())
        return PathFindingGrid(matrix=matrix)

    def get_closest(self, location1: Tuple[int, int], locations: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        get the closet of something from a list. ex: get the closest barn, get the closest person, etc.
        """
        if len(locations) == 0:
            return None
        check = deepcopy(locations)
        closest = None
        while not closest:
            if len(check) == 0:
                return None
            location2 = next(iter(check))
            if location2[0] == location1[0]:
                closest = location2
            else:
                check.remove(location2)
        if not closest:
            return None
        for location2 in locations:
            d1 = self.get_distance(location1, location2)
            d2 = self.get_distance(location1, closest)
            if d1 is None or d2 is None:
                continue
            if d1 < d2:
                closest = location2
        return closest

    def get_furthest(self, location1: Tuple[int, int], locations: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        get the furthest of something from a list. ex: get the furthest barn, get the furthest person, etc.
        """
        if len(locations) == 0:
            return None
        furthest = next(iter(locations))
        for location2 in locations:
            d1 = self.get_distance(location1, location2)
            d2 = self.get_distance(location1, furthest)
            if d1 is None or d2 is None:
                continue
            if d1 > d2:
                furthest = location2
        return furthest

    @staticmethod
    def get_distance(location1: Tuple[int, int], location2: Tuple[int, int]) -> Optional[float]:
        if not location1 or not location2:
            return None
        x1 = location1[1]
        y1 = location1[2]
        x2 = location2[1]
        y2 = location2[2]
        return (((x1 - x2) ** 2) + ((y1 - y2) ** 2)) ** 0.5

    @staticmethod
    def _is_one_away(location1: Tuple[int, int], location2: Tuple[int, int]) -> bool:
        if not location1 or not location2:
            return False
        if not isinstance(location1, tuple) or not isinstance(location2, tuple):
            return False
        a = abs(location1[1] - location2[1])
        b = abs(location1[2] - location2[2])
        if a > 1 or b > 1:
            return False
        return True

    def is_next_to(self, locations: List[Tuple[int, int]]) -> bool:
        for location in locations:
            if self._is_one_away(self._person.get_location(), location):
                return True
        return False

    def is_near(self, location1: Tuple[int, int], location2: Tuple[int, int], distance: int = 5) -> bool:
        if not location1 or not location2:
            return False
        d1 = self.get_distance(location1, location2)
        if d1:
            if d1 < distance:
                return True
        return False

    def can_get_to_location(self, location: Tuple[int, int]) -> bool:
        grid = self._get_path_finding_grid()
        path = self._get_path(location, grid)
        if path:
            return True
        return False
