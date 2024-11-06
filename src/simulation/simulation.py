from src.simulation.grid.grid import Grid
from src.simulation.people.people import People

from src.simulation.result.stats import Stats


class Simulation:
    def __init__(
        self, actions_per_day: int, days_per_year: int, years: int, grid_size: int
    ) -> None:
        self._days_per_year: int = days_per_year
        self._years: int = years
        self._grid: Grid = Grid(grid_size)
        self._people: People = People(self, actions_per_day)

    def run(self) -> Stats:
        stats: Stats = Stats()

        # TODO flesh out this logic
        days: int = self._years * self._days_per_year
        for day in range(days):
            self._people.take_actions_for_day()
            if day % self._days_per_year == 0:
                self._grid.grow_trees()
                # todo: add a disaster percentage chance (crops diseased, house burned, cemetary makes zombies, mines collapse, divorce, be preggers 'pregaganant')
                
                self._people.age()

        return stats

    def get_grid(self) -> Grid:
        return self._grid
