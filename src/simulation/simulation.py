from grid.grid import Grid
from people.people import People
from visualization.visualizer import Visualizer
from src.settings import settings

class Simulation:
    def __init__(
        self
    ) -> None:
        actions_per_day = settings.get("actions_per_day", 5)
        days_per_year = settings.get("days_per_year", 365)
        years = settings.get("years", 50)
        grid_size = settings.get("grid_size", 100)
        
        self._days_per_year: int = days_per_year
        self._years: int = years
        self._grid: Grid = Grid(self, grid_size)
        self._people: People = People(self, actions_per_day)
        self._max_days: int = self._years * self._days_per_year
        self._current_day: int = 0
        self._time: int = 0
        
    def increment_time(self) -> None:
        self._time += 1
        
    def get_time(self) -> int:
        return self._time

    def run(self) -> Visualizer:
        visualizer: Visualizer = Visualizer()
        for day in range(self._max_days):
            self._current_day += 1
            if len(self._people) == 0: # all the people dead
                break
            self._people.take_actions_for_day()
            self._grid.turn_completed_constructions_to_buildings()
            self._people.spouses_share_memory()  # end of day spouses talk
            self._people.kill_stuck()

            if self._has_been_a_year(day):
                self._people.swap_homes()
                self._people.age()
                self._people.make_babies()
                self._grid.grow_trees()
                self._create_disasters()
                visualizer.add(self._get_year(day), self._grid, self._people)
                self._people.flush()
                self._grid.flush()

        return visualizer

    def get_day(self) -> int:
        return self._current_day

    def _create_disasters(self):
        self._people.generate_disasters()
        self._grid.generate_disasters()

    def _has_been_a_year(self, day):
        return day % self._days_per_year == 0

    def _get_year(self, day: int) -> int:
        return day // self._days_per_year

    def get_current_time(self) -> int:
        return self._people.get_time()

    def get_grid(self) -> Grid:
        return self._grid

    def get_people(self) -> People:
        return self._people

    def get_people_object(self) -> People:
        return self._people
