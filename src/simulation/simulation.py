from src.logger import logger
from src.settings import settings
from src.simulation.grid.grid import Grid
from src.simulation.people.people import People
from src.simulation.visualization.visualizer import Visualizer


class Simulation:
    def __init__(self) -> None:
        logger.debug("Initializing simulation settings.")

        actions_per_day = settings.get("actions_per_day", 5)
        logger.debug(f"actions_per_day set to {actions_per_day}.")

        days_per_year = settings.get("days_per_year", 365)
        logger.debug(f"days_per_year set to {days_per_year}.")

        years = settings.get("years", 50)
        logger.debug(f"years set to {years}.")

        grid_size = settings.get("grid_size", 100)
        logger.debug(f"grid_size set to {grid_size}.")

        self._days_per_year: int = days_per_year
        logger.debug(f"self._days_per_year initialized to {self._days_per_year}.")

        self._actions_per_day: int = actions_per_day
        logger.debug(f"self._actions_per_day initialized to {self._actions_per_day}.")

        self._years: int = years
        logger.debug(f"self._years initialized to {self._years}.")

        self._grid: Grid = Grid(self, grid_size)
        logger.debug(f"Grid initialized with grid_size {grid_size}.")

        self._people: People = People(self, actions_per_day)
        logger.debug(f"People initialized with actions_per_day {actions_per_day}.")

        self._max_days: int = self._years * self._days_per_year
        logger.debug(f"self._max_days calculated as {self._max_days}.")

        self._day: int = 0
        logger.debug("self._day initialized to 0.")

        self._time: int = 0
        logger.debug("self._time initialized to 0.")

        # Log initializ

    def actions_per_year(self) -> int:
        result = self._days_per_year * self._actions_per_day
        logger.debug(
            f"Calculating actions_per_year: {self._days_per_year} days/year * {self._actions_per_day} actions/day = {result}."
        )
        return result

    def increment_time(self) -> None:
        logger.debug(f"Incrementing time. Current time: {self._time}.")
        self._time += 1
        logger.debug(f"Time incremented. New time: {self._time}.")

    def get_time(self) -> int:
        logger.debug(f"Retrieving current time: {self._time}.")
        return self._time

    def run(self) -> Visualizer:
        logger.info("Simulation started.")
        visualizer: Visualizer = Visualizer()

        for day in range(self._max_days):
            self._day = day
            logger.debug(f"Day {day} begins.")

            if len(self._people) == 0:  # all the people dead
                logger.info("Everybody died! Game over!")
                break

            logger.debug("People taking actions for the day.")
            self._people.take_actions_for_day()

            logger.debug("Grid processing completed constructions.")
            self._grid.turn_completed_constructions_to_buildings()

            logger.debug("Spouses sharing memory at the end of the day.")
            self._people.spouses_share_memory()

            logger.debug("Removing stuck people.")
            self._people.kill_stuck()

            if self._has_been_a_year(day):
                logger.debug(f"Year completed on day {day}. Performing yearly actions.")
                self._people.swap_homes()  # people want to live close to work
                logger.debug("People swapped homes.")
                
                self._people.age()
                logger.debug("People aged.")
                
                self._people.make_babies()
                logger.debug("New babies made.")
                
                self._grid.grow_trees()
                logger.debug("Grid growing trees.")
                
                self._create_disasters()
                logger.debug("Disasters created for the year.")

                year = self._get_year(day)
                logger.debug(f"Year {year} logged into the visualizer.")
                visualizer.add(year, self._grid, self._people)

                logger.debug("Flushing logs for end-of-year data.")
                self.flush()

        logger.info("Simulation ended.")
        return visualizer
    
    def flush(self) -> None:
        logger.debug("Flushing people and grid data...")
        self._people.flush()
        logger.debug("People data flushed.")
        self._grid.flush()
        logger.debug("Grid data flushed.")

    def get_day(self) -> int:
        logger.debug(f"Retrieving current day: {self._day}.")
        return self._day

    def _create_disasters(self) -> None:
        logger.debug("Creating disasters for people and grid...")
        self._people.generate_disasters()
        logger.debug("Disasters generated for people.")
        self._grid.generate_disasters()
        logger.debug("Disasters generated for grid.")

    def _has_been_a_year(self, day) -> bool:
        is_year = day % self._days_per_year == 0
        logger.debug(
            f"Checking if day {day} marks the end of a year. Days per year: {self._days_per_year}. Result: {is_year}."
        )
        return is_year

    def _get_year(self, day: int) -> int:
        year = day // self._days_per_year
        logger.debug(
            f"Calculating year from day {day}. Days per year: {self._days_per_year}. Year: {year}."
        )
        return year

    def get_grid(self) -> Grid:
        logger.debug("Retrieving grid object.")
        return self._grid

    def get_people(self) -> People:
        logger.debug("Retrieving people object.")
        return self._people

    def get_people_object(self) -> People:
        logger.debug("Retrieving people object (via get_people_object).")
        return self._people
