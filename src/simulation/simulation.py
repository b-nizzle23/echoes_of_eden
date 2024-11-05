from simulation.grid.grid import Grid
from simulation.people.people import People


class Simulation:
    def __init__(self, actions_per_day, days_per_year, years, grid_size):
        self._days_per_year = days_per_year
        self._years = years
        self._grid = Grid(grid_size)
        self._people = People(self, actions_per_day)

    def run(self):
        stats = {
            # TODO figure out what we care about
        }

        # TODO flesh out this logic
        days = self._years * self._days_per_year
        for day in range(days):
            self._people.take_actions_for_day()
            if day % self._days_per_year == 0:
                self._grid.grow_trees()
                self._people.age()

        return stats

    def get_grid(self):
        return self._grid
