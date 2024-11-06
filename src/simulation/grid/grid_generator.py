import random
from typing import List


class GridGenerator:
    def __init__(
        self,
        size: int,
        tree_density: float = 0.4,
        ca_iterations: int = 40,
    ) -> None:
        self._grid: List[List[str]] = []
        self._width: int = size
        self._height: int = size
        self._tree_density: float = tree_density
        self._ca_iterations: int = ca_iterations
        self._end_of_world_char: str = "e"
        self._tree_char: str = "*"

        # TODO generate town
        self.num_houses: int = 10
        self.num_farms: int = 3
        self.num_mines: int = 1
        self.num_barns: int = 1

    def generate(self) -> List[List[str]]:
        self._grid = [[" " for _ in range(self._width)] for _ in range(self._height)]
        self._add_clustered_trees()
        self._place_town_in_center()
        return self._grid

    def _place_town_in_center(self) -> None:
        town_layout = self._read_town_layout("../../../data/town.txt")
        town_width = len(town_layout[0])
        town_height = len(town_layout)
        town_x = (self._width - town_width) // 2
        town_y = (self._height - town_height) // 2

        # Place the town layout on the grid
        for y in range(town_height):
            for x in range(town_width):
                self._grid[town_y + y][town_x + x] = town_layout[y][x]

    @staticmethod
    def _read_town_layout(filename: str) -> List[str]:
        town_layout: List[str] = []
        max_length: int = 0

        with open(filename, "r") as file:
            for line in file.readlines():
                row = line.rstrip("\n")
                if row:
                    town_layout.append(row)
                    max_length = max(max_length, len(row))

        # Pad each row to make them the same length
        for i in range(len(town_layout)):
            town_layout[i] = town_layout[i].ljust(max_length)

        return town_layout

    def _add_clustered_trees(self) -> None:
        self._create_outer_wall()
        self._generate_inner_trees()
        self._do_cellular_automata()

    def _create_outer_wall(self) -> None:
        self._grid[0] = [self._end_of_world_char] * len(self._grid[0])
        self._grid[-1] = [self._end_of_world_char] * len(self._grid[-1])
        for i in range(len(self._grid)):
            self._grid[i][0] = self._end_of_world_char
            self._grid[i][-1] = self._end_of_world_char

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
        count: int = 0
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
