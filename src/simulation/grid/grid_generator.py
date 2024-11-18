import random
from typing import List, Tuple

from src.settings import settings
from src.logger import logger

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

        # Log the initialization parameters
        logger.debug("GridGenerator initialized with the following parameters:")
        logger.debug(f"Grid size: {self._width}x{self._height}")
        logger.debug(f"Tree density: {self._tree_density}")
        logger.debug(f"CA iterations: {self._ca_iterations}")
        logger.debug(f"Town clearance radius: {self._town_clearance_radius}")
        logger.debug(f"Building buffer: {self._building_buffer}")
        logger.debug(f"Building sizes: {self._building_sizes}")
        logger.debug(f"Number of houses: {self._num_houses}")
        logger.debug(f"Number of farms: {self._num_farms}")
        logger.debug(f"Number of barns: {self._num_barns}")
        logger.debug(f"Number of mines: {self._num_mines}")

    def generate(self) -> List[List[str]]:
        logger.debug("Starting grid generation process...")

        # Initialize the grid (empty)
        logger.debug("Initializing the grid...")
        self._initialize_grid()

        # Add clustered trees based on tree density
        logger.debug(f"Adding clustered trees with density {self._tree_density}...")
        self._add_clustered_trees()

        # Generate the town layout, placing buildings
        logger.debug("Generating the town layout with buildings...")
        self._generate_town()

        logger.debug("Grid generation completed.")
        return self._grid

    def _initialize_grid(self) -> None:
        logger.debug("Initializing grid with size %d x %d...", self._width, self._height)

        # Initialize grid with empty spaces
        self._grid = [[" " for _ in range(self._width)] for _ in range(self._height)]

        logger.debug("Grid initialized successfully with empty spaces.")

    def _generate_town(self) -> None:
        logger.debug("Generating town at the center of the grid...")

        center_x, center_y = self._width // 2, self._height // 2
        self._clear_town_area(center_x, center_y)

        buildings = [
            (
                settings.get("home_char", "H"),
                self._num_houses,
                settings.get("home_completion_prob", 0.8)
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
            logger.debug("Placing %d buildings of type '%s' with a completion probability of %.2f...",
                         count, building_type, completion_prob)
            self._place_building_random(building_type, True)  # Place the first building (always completed)
            for i in range(count - 1):
                is_completed = random.random() < completion_prob
                logger.debug("Building %d/%d of type '%s' - Completed: %s", i + 1, count - 1, building_type,
                             is_completed)
                self._place_building_random(building_type, is_completed)

        logger.debug("Town generation completed with %d homes, %d farms, %d barns, and %d mines placed.",
                     self._num_houses, self._num_farms, self._num_barns, self._num_mines)

    def _clear_town_area(self, center_x: int, center_y: int) -> None:
        logger.debug("Clearing town area with radius %d around (%d, %d)...", self._town_clearance_radius, center_x,
                     center_y)
        radius = self._town_clearance_radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = center_x + dx, center_y + dy
                if 0 <= x < self._width and 0 <= y < self._height:
                    self._grid[y][x] = " "
        logger.debug("Town area cleared.")

    def _place_building_random(self, building_type: str, is_completed: bool) -> None:
        logger.debug("Placing building of type '%s' (Completed: %s)...", building_type, is_completed)
        center_x, center_y = self._width // 2, self._height // 2
        width, height = self._building_sizes[building_type]

        # Search for a random location to place the building, expanding outward
        for distance in range(1, max(self._width, self._height)):
            for dy in range(-distance, distance + 1):
                for dx in range(-distance, distance + 1):
                    x, y = center_x + dx, center_y + dy
                    if 0 <= x < self._width and 0 <= y < self._height:
                        if self._can_place_building(x, y, width, height):
                            building_char = (
                                building_type if is_completed else building_type.lower()
                            )
                            logger.debug("Placing building at (%d, %d)", x, y)
                            self._clear_area(x, y, width, height)
                            self._place_on_grid(x, y, width, height, building_char)
                            logger.debug("Building placed.")
                            return
        logger.warning("Failed to place building of type '%s' after searching the grid.", building_type)

    def _can_place_building(self, x: int, y: int, width: int, height: int) -> bool:
        logger.debug("Checking if building can be placed at (%d, %d) with size (%d, %d)...", x, y, width, height)

        if x + width > self._width or y + height > self._height:
            logger.debug("Building exceeds grid boundaries.")
            return False

        for dy in range(-self._building_buffer, height + self._building_buffer):
            for dx in range(-self._building_buffer, width + self._building_buffer):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self._width and 0 <= new_y < self._height:
                    if self._grid[new_y][new_x] != " ":
                        logger.debug("Blocked by non-empty cell at (%d, %d). Cannot place building here.", new_x, new_y)
                        return False
        logger.debug("Building can be placed at (%d, %d).", x, y)
        return True

    def _clear_area(self, x: int, y: int, width: int, height: int) -> None:
        logger.debug("Clearing area around (%d, %d) with size (%d, %d)...", x, y, width, height)

        for dy in range(-self._building_buffer, height + self._building_buffer):
            for dx in range(-self._building_buffer, width + self._building_buffer):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self._width and 0 <= new_y < self._height:
                    if self._grid[new_y][new_x] == self._tree_char:
                        logger.debug("Clearing tree at (%d, %d).", new_x, new_y)
                        self._grid[new_y][new_x] = " "
                    elif self._grid[new_y][new_x] == " ":
                        logger.debug("Cell at (%d, %d) is already empty.", new_x, new_y)
                        self._grid[new_y][new_x] = " "
        logger.debug("Area cleared.")

    def _place_on_grid(
            self, x: int, y: int, width: int, height: int, building_char: str
    ) -> None:
        logger.debug("Placing building of type '%s' at (%d, %d) with size (%d, %d)...", building_char, x, y, width,
                     height)

        for dy in range(height):
            for dx in range(width):
                self._grid[y + dy][x + dx] = building_char
                logger.debug("Placed '%s' at position (%d, %d).", building_char, x + dx, y + dy)

        logger.debug("Building placed at (%d, %d).", x, y)

    def _add_clustered_trees(self) -> None:
        logger.debug("Starting tree clustering with density %.2f.", self._tree_density)
        self._generate_inner_trees()
        self._do_cellular_automata()
        logger.debug("Tree clustering completed.")

    def _generate_inner_trees(self) -> None:
        logger.debug("Generating trees within the grid...")
        for i in range(2, len(self._grid) - 2):
            for j in range(2, len(self._grid[i]) - 2):
                if random.random() < self._tree_density:
                    self._grid[i][j] = self._tree_char
                    logger.debug("Planted tree at (%d, %d).", j, i)
        logger.debug("Tree generation complete.")

    def _do_cellular_automata(self) -> None:
        logger.debug("Starting cellular automata with %d iterations.", self._ca_iterations)

        for iteration in range(self._ca_iterations):
            logger.debug("Iteration %d of %d...", iteration + 1, self._ca_iterations)

            grid_copy = [row[:] for row in self._grid]
            for i in range(2, len(self._grid) - 2):
                for j in range(2, len(self._grid[i]) - 2):
                    count = self._count_number_of_neighbors(i, j)
                    logger.debug("Cell (%d, %d) has %d neighbors.", i, j, count)

                    if self._grid[i][j] == self._tree_char and count < 3:
                        grid_copy[i][j] = " "
                        logger.debug("Cell (%d, %d) has fewer than 3 neighbors, removing tree.", i, j)
                    elif self._grid[i][j] == " " and count > 4:
                        grid_copy[i][j] = self._tree_char
                        logger.debug("Cell (%d, %d) has more than 4 neighbors, adding tree.", i, j)

            self._grid = grid_copy
            logger.debug("Iteration %d complete.", iteration + 1)

        logger.debug("Cellular automata process completed.")

    def _count_number_of_neighbors(self, row: int, col: int) -> int:
        count = 0
        logger.debug("Counting neighbors for cell (%d, %d)...", row, col)

        for i in range(-1, 2):
            for j in range(-1, 2):
                if (
                    (i == 0 and j == 0)  # Skip the cell itself
                    or not (0 <= row + i < len(self._grid))  # Out of bounds check
                    or not (0 <= col + j < len(self._grid[row]))  # Out of bounds check
                ):
                    continue
                if self._grid[row + i][col + j] == self._tree_char:
                    count += 1
                    logger.debug("Neighbor at (%d, %d) is a tree.", row + i, col + j)

        logger.debug("Cell (%d, %d) has %d tree neighbors.", row, col, count)
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
