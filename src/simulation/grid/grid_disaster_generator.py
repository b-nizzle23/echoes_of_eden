from __future__ import annotations

import random
from typing import TYPE_CHECKING, List, Dict

from src.logger import logger
from src.simulation.grid.location import Location
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.work.farm import Farm
from src.simulation.grid.structure.work.mine import Mine

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.structure.structure import Structure


class GridDisasterGenerator:
    def __init__(self, grid: Grid):
        self._grid = grid
        # Initialize counters for each disaster type
        self._disaster_counts: Dict[str, int] = {
            'rats_eat_home_food': 0,
            'burn_buildings': 0,
            'decrease_farm_yield': 0,
            'decrease_mine_yield': 0,
            'forest_fire': 0,
            'steal_barn_resources': 0
        }

        # Log the initialization of the disaster generator
        logger.debug("Initialized GridDisasterGenerator.")
        logger.debug(f"Initial disaster counts: {self._disaster_counts}")

    def generate(self, chance: float) -> None:
        """Randomly trigger one of the disaster types with a given chance."""
        if random.random() < chance:
            severity = random.randint(1, 10)

            # Log the generation of a disaster
            logger.debug(f"Disaster generated with severity {severity}.")

            # List of disaster methods
            disaster_methods = [
                (self._rats_eat_home_food, 'rats_eat_home_food'),
                (self._burn_buildings, 'burn_buildings'),
                (self._decrease_farm_yield, 'decrease_farm_yield'),
                (self._decrease_mine_yield, 'decrease_mine_yield'),
                (self._forest_fire, 'forest_fire'),
                (self._steal_barn_resources, 'steal_barn_resources'),
            ]

            # Randomly pick one disaster to trigger
            chosen_disaster, disaster_name = random.choice(disaster_methods)
            logger.debug(f"Triggering disaster: {disaster_name}.")
            chosen_disaster(severity)

            # Increment the disaster count for the chosen disaster
            self._disaster_counts[disaster_name] += 1
            logger.debug(f"Disaster count for {disaster_name}: {self._disaster_counts[disaster_name]}.")

    def get_disaster_counts(self) -> Dict[str, int]:
        """Return the current disaster count statistics."""
        return self._disaster_counts

    def flush(self):
        """Reset all disaster counters to 0."""
        logger.debug("Resetting disaster counters.")
        for disaster in self._disaster_counts:
            self._disaster_counts[disaster] = 0

    def _rats_eat_home_food(self, severity: int) -> None:
        """Remove food from home storage based on disaster severity."""
        logger.debug(f"Rats are eating home food with severity {severity}.")
        affected_homes_percent = (severity // 2) / 10
        homes: List[Structure] = self._grid.get_structures(Home)
        num_affected = int(len(homes) * affected_homes_percent)
        logger.debug(f"Number of homes affected: {num_affected}/{len(homes)}.")

        homes_affected = random.sample(homes, num_affected)
        for home in homes_affected:
            resources: List[str] = home.get_resource_names()
            for resource in resources:
                logger.debug(f"Removing resource {resource} from home at {home.get_location()}.")
                home.remove_resource(resource, home.get_resource(resource))

    def _burn_buildings(self, severity: int) -> None:
        """Burn down buildings based on severity."""
        logger.debug(f"Burning buildings with severity {severity}.")
        buildings_burned_percent = (severity // 2) / 10
        buildings: List[Structure] = list(self._grid.get_buildings().values())
        random.shuffle(buildings)

        num_buildings_to_process = int(len(buildings) * buildings_burned_percent)
        logger.debug(f"Number of buildings to process: {num_buildings_to_process}/{len(buildings)}.")

        buildings_to_burn = buildings[:num_buildings_to_process]

        for building in buildings_to_burn:
            logger.debug(f"Burning building at {building.get_location()}.")
            if random.choice([True, False]):
                self._grid.remove(building)
                logger.debug(f"Building at {building.get_location()} burned down.")
            else:
                self._grid.remove(building, True)
                logger.debug(f"Building at {building.get_location()} burned down and deconstructed.")

    def _decrease_farm_yield(self, severity: int) -> None:
        """Disease infects the farm, reducing resources or crops."""
        logger.debug(f"Decreasing farm yield with severity {severity}.")
        farms_diseased_percent = (severity // 2) / 10
        farms: List[Structure] = self._grid.get_structures(Farm)
        num_affected = int(len(farms) * farms_diseased_percent)
        logger.debug(f"Number of farms affected: {num_affected}/{len(farms)}.")

        farms_affected = random.sample(farms, num_affected)
        for farm in farms_affected:
            logger.debug(f"Decreasing yield for farm at {farm.get_location()}.")
            farm.decrease_yield()

    def _decrease_mine_yield(self, severity: int) -> None:
        logger.debug(f"Decreasing mine yield with severity {severity}.")
        percent_affected = (severity // 2) / 10
        mines: List[Structure] = self._grid.get_structures(Mine)
        num_affected = int(len(mines) * percent_affected)
        logger.debug(f"Number of mines affected: {num_affected}/{len(mines)}.")

        mines_affected = random.sample(mines, num_affected)
        for mine in mines_affected:
            logger.debug(f"Decreasing yield for mine at {mine.get_location()}.")
            mine.decrease_yield()

    def _forest_fire(self, severity: int) -> None:
        logger.debug(f"Starting forest fire with severity {severity}.")
        max_width = self._grid.get_width()
        max_height = self._grid.get_height()

        burned_width = (severity * max_width) // 10
        burned_height = (severity * max_height) // 10

        burned_width = min(burned_width, max_width)
        burned_height = min(burned_height, max_height)

        start_x = random.randint(0, max_width - burned_width)
        start_y = random.randint(0, max_height - burned_height)

        removal_probability = severity * 0.1
        logger.debug(f"Burned area: width {burned_width}, height {burned_height}, starting at ({start_x}, {start_y}).")
        logger.debug(f"Chance of tree removal: {removal_probability * 100}%.")

        for x in range(start_x, start_x + burned_width):
            for y in range(start_y, start_y + burned_height):
                location = Location(x, y)

                if self._grid.is_tree(location) and random.random() <= removal_probability:
                    logger.debug(f"Tree at {location} removed by fire.")
                    self._grid.remove(self._grid.get_structure(location))

    def _steal_barn_resources(self, severity: int) -> None:
        logger.debug(f"Stealing barn resources with severity {severity}.")
        percent_affected = (severity // 2) / 10
        barns: List[Structure] = self._grid.get_structures(Barn)
        num_affected = int(len(barns) * percent_affected)
        logger.debug(f"Number of barns affected: {num_affected}/{len(barns)}.")

        barns_affected = random.sample(barns, num_affected)
        for barn in barns_affected:
            if isinstance(barn, Barn):
                resources: List[str] = barn.get_resource_names()
                for resource in resources:
                    logger.debug(f"Stealing resource {resource} from barn at {barn.get_location()}.")
                    barn.remove_resource(resource, barn.get_resource(resource))
