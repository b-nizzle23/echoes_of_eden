from .memory import Memory
from simulation.grid.grid import Grid


class Vision:
    def __init__(self, person, grid: Grid, visibility):
        self._person = person
        self._grid = grid
        self._visibility = visibility

    def look_around(self):
        what_is_around = Memory()
        self._search(self._person.get_location(), self._visibility, what_is_around, [])
        return what_is_around

    def _search(self, location, visibility, what_is_around, blocked):
        if visibility <= 0:
            return
        if location in blocked:
            return
        x = location[0]
        y = location[1]
        blocked.append((x, y))
        for i in range(-1, 2):
            for j in range(-1, 2):
                a = x + i
                b = y + j
                if self._is_out_of_bounds(a, b) or self._is_blocked(blocked, a, b):
                    continue
                self._add_to_memory(what_is_around, blocked, i, j, a, b)
                self._search((a, b), visibility - 1, what_is_around, blocked)

    def _add_to_memory(self, what_is_around, blocked, i, j, a, b):
        location = (a, b)
        if not self._grid.is_location_in_bounds(location):
            return
        if self._grid.is_barn(location):
            what_is_around.add("barns", location)
            self._block(blocked, i, j, a, b)
        if self._grid.is_construction_barn(location):
            what_is_around.add("construction_barns", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_home(location):
            what_is_around.add("homes", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_construction_home(location):
            what_is_around.add("construction_homes", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_farm(location):
            what_is_around.add("farms", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_construction_farm(location):
            what_is_around.add("construction_farms", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_mine(location):
            what_is_around.add("mines", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_construction_mine(location):
            what_is_around.add("construction_mines", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_tree(location):
            what_is_around.add("trees", location)
            self._block(blocked, i, j, a, b)
        elif self._grid.is_empty(location):
            what_is_around.add("empties", location)
        else:
            raise Exception("I see a char you didn't tell me about")

    def _is_out_of_bounds(self, x, y):
        return (
            x < 0
            or y < 0
            or x >= self._grid.get_width()
            or y >= self._grid.get_height()
        )

    def _block(self, blocked, i, j, a, b):
        blocked.append((a, b))
        if not self._is_diagonal(i, j):
            direction = self._get_direction(i, j)
            if direction == "l":
                for k in range(a, 0, -1):
                    blocked.append((a + k, b))
            elif direction == "r":
                for k in range(a, self._grid.get_width()):
                    blocked.append((a + k, b))
            elif direction == "d":
                for k in range(b, self._grid.get_height()):
                    blocked.append((a, b + k))
            elif direction == "u":
                for k in range(b, 0, -1):
                    blocked.append((a, b + k))

    @staticmethod
    def _is_blocked(blocked, x, y):
        return (x, y) in blocked

    @staticmethod
    def _is_diagonal(i, j):
        return i < 0 < j or j < 0 < i or (i < 0 and j < 0) or (i > 0 and j > 0)

    @staticmethod
    def _get_direction(i, j):
        if i == 0 and j == 1:
            return "r"
        if i == 0 and j == -1:
            return "l"
        if i == 1 and j == 0:
            return "u"
        if i == -1 and j == 0:
            return "d"
        else:
            raise Exception("invalid coordinates")
