from simulation.grid.grid_generator import GridGenerator


class Grid:
    def __init__(self, size):
        grid_generator = GridGenerator(size)
        self._width = size
        self._height = size
        self._grid = grid_generator.generate()
        self.buildings = self._find_buildings()

    def _find_buildings(self):
        # TODO scan the grid and find the starting buildings, make sure a group of b's are all mapped to the same barn instance
        return {}

    def is_valid_location_for_person(self, location):
        # TODO check if a person could stand there (not on a tree or building)
        pass

    def is_location_in_bounds(self, location):
        pass

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def __str__(self):
        s = ""
        for row in self._grid:
            s += " ".join(row) + "\n"
        return s

    def grow_trees(self):
        # TODO scan the grid and for every tree found there is a chance that a tree will grow next to it
        pass

    def chop_down_tree(self, x, y):
        if not self.is_tree(x, y):
            raise Exception("tried to chop down not a tree")
        self._grid[y][x] = " "
        return 100

    def get_path_finding_matrix(self):
        # TODO return a 2d array of numbers
        # look at https://github.com/brean/python-pathfinding/blob/main/docs/01_basic_usage.md for more details
        pass

    def is_tree(self, location):
        self._is_item(location[0], location[1], "*")

    def is_barn(self, location):
        self._is_item(location[0], location[1], "B")

    def is_construction_barn(self, location):
        self._is_item(location[0], location[1], "b")

    def is_home(self, location):
        self._is_item(location[0], location[1], "H")

    def is_construction_home(self, location):
        self._is_item(location[0], location[1], "h")

    def is_farm(self, location):
        self._is_item(location[0], location[1], "F")

    def is_construction_farm(self, location):
        self._is_item(location[0], location[1], "f")

    def is_mine(self, location):
        self._is_item(location[0], location[1], "M")

    def is_construction_mine(self, location):
        self._is_item(location[0], location[1], "m")

    def is_empty(self, location):
        self._is_item(location[0], location[1], " ")

    def _is_item(self, x, y, char):
        return self._grid[y][x] == char


if __name__ == "__main__":
    grid = Grid(75)
    print(grid)
