from typing import Dict, List

from grid_generator import GridGenerator
from location import Location


class Grid:
    def __init__(self, size: int) -> None:
        grid_generator = GridGenerator(size)
        self._width: int = size
        self._height: int = size
        self._grid: List[List[str]] = grid_generator.generate()
        self.buildings: Dict[str, List[Location]] = self._find_buildings()

    def _find_buildings(self) -> Dict[str, List[Location]]:
        buildings: Dict[str, List[Location]] = {}
        for y in range(self._height):
            for x in range(self._width):
                cell = self._grid[y][x]
                if cell != " ":
                    location = Location(x, y)  # Create Location object
                    if cell not in buildings:
                        buildings[cell] = []
                    buildings[cell].append(location)
        return buildings

    def is_valid_location_for_person(self, location: Location) -> bool:
        if not self.is_location_in_bounds(location):
            return False
        if self.is_tree(location) or any(
            self.is_building(location, building) for building in self.buildings
        ):
            return False
        return True

    def is_location_in_bounds(self, location: Location) -> bool:
        return 0 <= location.x < self._width and 0 <= location.y < self._height

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def __str__(self) -> str:
        return "\n".join(" ".join(row) for row in self._grid)

    def grow_trees(self) -> None:
        pass

    def chop_down_tree(self, location: Location) -> int:
        if not self.is_tree(location):
            raise Exception(f"Tried to chop down a non-tree at location {location}")
        self._grid[location.y][location.x] = " "
        return 100

    def get_path_finding_matrix(self) -> List[List[int]]:
        pass

    def is_tree(self, location: Location) -> bool:
        return self._is_item(location, "*")

    def is_barn(self, location: Location) -> bool:
        return self._is_item(location, "B")

    def is_construction_barn(self, location: Location) -> bool:
        return self._is_item(location, "b")

    def is_home(self, location: Location) -> bool:
        return self._is_item(location, "H")

    def is_construction_home(self, location: Location) -> bool:
        return self._is_item(location, "h")

    def is_farm(self, location: Location) -> bool:
        return self._is_item(location, "F")

    def is_construction_farm(self, location: Location) -> bool:
        return self._is_item(location, "f")

    def is_mine(self, location: Location) -> bool:
        return self._is_item(location, "M")

    def is_construction_mine(self, location: Location) -> bool:
        return self._is_item(location, "m")

    def is_empty(self, location: Location) -> bool:
        return self._is_item(location, " ")

    def is_building(self, location: Location, building_char: str) -> bool:
        return self._is_item(location, building_char)

    def _is_item(self, location: Location, char: str) -> bool:
        return self._grid[location.y][location.x] == char


if __name__ == "__main__":
    grid = Grid(75)
    print(grid)
