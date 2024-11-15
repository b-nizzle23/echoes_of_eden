import random
from typing import List, Tuple

from src.settings import settings


class GridGenerator:
    def __init__(
        self,
        size: int,
        tree_density: float = settings.get("tree_density", 0.4),
        ca_iterations: int = settings.get("ca_iterations", 40),
        town_clearance_radius: int = settings.get("town_clearance_radius", 15),
        building_buffer: int = settings.get("building_buffer", 1),
    ) -> None:
        self._grid: List[List[str]] = []
        self._width: int = size
        self._height: int = size
        self._tree_density: float = tree_density
        self._ca_iterations: int = ca_iterations
        self._tree_char: str = settings.get("tree_char", "*")

        self._num_houses: int = random.randint(
            settings.get("num_house_min", 3),
            settings.get("num_house_max", 8)
        )
        self._num_farms: int = random.randint(
            settings.get("num_farm_min", 1),
            settings.get("num_farm_max", 3)
        )
        self._num_barns: int = random.randint(
            settings.get("num_barn_min", 1),
            settings.get("num_barn_max", 2)
        )
        self._num_mines: int = random.randint(
            settings.get("num_mines_min", 1),
            settings.get("num_mines_max", 2)
        )

        self._building_sizes: dict[str, Tuple[int, int]] = {
            settings.get("home_char", "H"): (
                settings.get("home_size", 2),
                settings.get("home_size", 2)
            ),
            settings.get("farm_char", "F"): (
                settings.get("farm_size", 5),
                settings.get("farm_size", 5)
            ),
            settings.get("barn_char", "B"): (
                settings.get("barn_size", 3),
                settings.get("barn_size", 3)
            ),
            settings.get("mine_char", "M"): (
                settings.get("mine_size", 3),
                settings.get("mine_size", 3)
            ),
        }

        self._town_clearance_radius: int = town_clearance_radius
        self._building_buffer: int = building_buffer

    def generate(self) -> List[List[str]]:
        self._initialize_grid()
        self._add_clustered_trees()
        self._generate_town()
        return self._grid

    def _initialize_grid(self) -> None:
        # Initialize grid with empty spaces
        self._grid = [[" " for _ in range(self._width)] for _ in range(self._height)]

    def _generate_town(self) -> None:
        center_x, center_y = self._width // 2, self._height // 2
        self._clear_town_area(center_x, center_y)

        buildings = [
            (
                settings.get("home_char", "H"),
                self._num_houses,
                settings.get("home_completion_prob",0.8)
            ),
            (
                settings.get("farm_char", "F"),
                self._num_farms,
                settings.get("farm_completion_prob", 0.8)
            ),
            (
                settings.get("barn_char", "B"),
                self._num_barns,
                settings.get("barn_completion_prob", 0.8)
            ),
            (
                settings.get("mine_char", "M"),
                self._num_mines,
                settings.get("mine_completion_prob", 0.8)
            )
        ]

        for building_type, count, completion_prob in buildings:
            self._place_building_random(building_type, True)
            for _ in range(count - 1):
                is_completed = random.random() < completion_prob
                self._place_building_random(building_type, is_completed)

    def _clear_town_area(self, center_x: int, center_y: int) -> None:
        radius = self._town_clearance_radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = center_x + dx, center_y + dy
                if 0 <= x < self._width and 0 <= y < self._height:
                    self._grid[y][x] = " "

    def _place_building_random(self, building_type: str, is_completed: bool) -> None:
        center_x, center_y = self._width // 2, self._height // 2
        width, height = self._building_sizes[building_type]
        for distance in range(1, max(self._width, self._height)):
            for dy in range(-distance, distance + 1):
                for dx in range(-distance, distance + 1):
                    x, y = center_x + dx, center_y + dy
                    if 0 <= x < self._width and 0 <= y < self._height:
                        if self._can_place_building(x, y, width, height):
                            building_char = (
                                building_type if is_completed else building_type.lower()
                            )
                            self._clear_area(x, y, width, height)
                            self._place_on_grid(x, y, width, height, building_char)
                            return

    def _can_place_building(self, x: int, y: int, width: int, height: int) -> bool:
        if x + width > self._width or y + height > self._height:
            return False
        for dy in range(-self._building_buffer, height + self._building_buffer):
            for dx in range(-self._building_buffer, width + self._building_buffer):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self._width and 0 <= new_y < self._height:
                    if self._grid[new_y][new_x] != " ":
                        return False
        return True

    def _clear_area(self, x: int, y: int, width: int, height: int) -> None:
        for dy in range(-self._building_buffer, height + self._building_buffer):
            for dx in range(-self._building_buffer, width + self._building_buffer):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self._width and 0 <= new_y < self._height:
                    if self._grid[new_y][new_x] == self._tree_char:
                        self._grid[new_y][new_x] = " "
                    if self._grid[new_y][new_x] == " ":
                        self._grid[new_y][new_x] = " "

    def _place_on_grid(
        self, x: int, y: int, width: int, height: int, building_char: str
    ) -> None:
        for dy in range(height):
            for dx in range(width):
                self._grid[y + dy][x + dx] = building_char

    def _add_clustered_trees(self) -> None:
        self._generate_inner_trees()
        self._do_cellular_automata()

    def _generate_inner_trees(self) -> None:
        for i in range(2, len(self._grid) - 2):
            for j in range(2, len(self._grid[i]) - 2):
                if random.random() < self._tree_density:
                    self._grid[i][j] = self._tree_char

    def _do_cellular_automata(self) -> None:
        for _ in range(self._ca_iterations):
            grid_copy = [row[:] for row in self._grid]
            for i in range(2, len(self._grid) - 2):
                for j in range(2, len(self._grid[i]) - 2):
                    count = self._count_number_of_neighbors(i, j)
                    if self._grid[i][j] == self._tree_char and count < 3:
                        grid_copy[i][j] = " "
                    elif self._grid[i][j] == " " and count > 4:
                        grid_copy[i][j] = self._tree_char
            self._grid = grid_copy

    def _count_number_of_neighbors(self, row: int, col: int) -> int:
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (
                    (i == 0 and j == 0)
                    or not (0 <= row + i < len(self._grid))
                    or not (0 <= col + j < len(self._grid[row]))
                ):
                    continue
                if self._grid[row + i][col + j] == self._tree_char:
                    count += 1
        return count


def print_grid(grid: List[List[str]]) -> None:
    # Top border: Adjusted to account for spaces between characters
    border = "+" + "-" * ((len(grid[0]) - 1) * 2 + 1) + "+"
    print(border)

    # Print each row with spaces between characters
    for row in grid:
        print("|" + " ".join(row) + "|")

    # Bottom border: Same as top border
    print(border)


if __name__ == "__main__":
    grid_size = 50  # You can set any size you want
    generator = GridGenerator(size=grid_size)
    generated_grid = generator.generate()

    print_grid(generated_grid)
