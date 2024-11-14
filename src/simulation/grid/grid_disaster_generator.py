import random
from typing import List, Dict

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.structure.work.farm import Farm
from src.simulation.grid.structure.work.mine import Mine


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

    def generate(self, chance: float) -> None:
        """Randomly trigger one of the disaster types with a given chance."""
        if random.random() < chance:
            severity = random.randint(1, 10)

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
            chosen_disaster(severity)

            # Increment the disaster count for the chosen disaster
            self._disaster_counts[disaster_name] += 1

    def get_disaster_counts(self) -> Dict[str, int]:
        """Return the current disaster count statistics."""
        return self._disaster_counts

    def flush(self):
        """Reset all disaster counters to 0."""
        for disaster in self._disaster_counts:
            self._disaster_counts[disaster] = 0

    def _rats_eat_home_food(self, severity: int) -> None:
        """Remove food from home storage based on disaster severity."""
        affected_homes_percent = (severity // 2) / 10
        homes: List[Structure] = self._grid.get_structures(Home)
        num_affected = int(len(homes) * affected_homes_percent)
        homes_affected = random.sample(homes, num_affected)
        for home in homes_affected:
            resources: List[str] = home.get_resource_names()
            for resource in resources:
                home.remove_resource(resource, home.get_resource(resource))

    def _burn_buildings(self, severity: int) -> None:
        """Burn down buildings based on severity."""
        buildings_burned_percent = (severity // 2) / 10
        buildings: List[Structure] = list(self._grid.get_buildings().values())
        random.shuffle(buildings)

        num_buildings_to_process = int(len(buildings) * buildings_burned_percent)

        buildings_to_burn = buildings[:num_buildings_to_process]

        for building in buildings_to_burn:
            if random.choice([True, False]):
                self._grid.remove(building)
            else:
                self._grid.remove(building, True)

    def _decrease_farm_yield(self, severity: int) -> None:
        """Disease infects the farm, reducing resources or crops."""
        farms_diseased_percent = (severity // 2) / 10
        farms: List[Structure] = self._grid.get_structures(Farm)
        num_affected = int(len(farms) * farms_diseased_percent)
        farms_affected = random.sample(farms, num_affected)
        for farm in farms_affected:
            farm.decrease_yield()

    def _decrease_mine_yield(self, severity: int) -> None:
        percent_affected = (severity // 2) / 10
        mines: List[Structure] = self._grid.get_structures(Mine)
        num_affected = int(len(mines) * percent_affected)
        mines_affected = random.sample(mines, num_affected)
        for mine in mines_affected:
            mine.decrease_yield()

    def _forest_fire(self, severity: int) -> None:
        """Forest fire destroys trees or forest resources, with a chance based on severity."""
        # Determine the width and height of the affected area based on severity (1-10)
        max_width = self._grid.get_width()
        max_height = self._grid.get_height()

        # Calculate width and height of the burned area as a percentage of the grid size
        burned_width = (severity * max_width) // 10
        burned_height = (severity * max_height) // 10

        # Ensure the burned area is within the bounds of the grid
        burned_width = min(burned_width, max_width)
        burned_height = min(burned_height, max_height)

        # Randomly select a starting point for the fire within the grid bounds
        start_x = random.randint(0, max_width - burned_width)
        start_y = random.randint(0, max_height - burned_height)

        # Calculate the probability of removing a tree based on severity
        # Higher severity gives a higher chance (severity 10 = 100% chance)
        removal_probability = severity * 0.1  # 10% chance for severity 1, 100% for severity 10

        # Iterate over the area affected by the fire
        for x in range(start_x, start_x + burned_width):
            for y in range(start_y, start_y + burned_height):
                location = Location(x, y)

                # Check if there's a tree at the location
                if self._grid.is_tree(location) and random.random() <= removal_probability:
                    # Generate a random number between 0 and 1 and compare to removal_probability
                    self._grid.remove(self._grid.get_structure(location))

    def _steal_barn_resources(self, severity: int) -> None:
        """Theft reduces resources in the barn based on severity."""
        percent_affected = (severity // 2) / 10
        barns: List[Structure] = self._grid.get_structures(Barn)
        num_affected = int(len(barns) * percent_affected)
        barns_affected = random.sample(barns, num_affected)
        for barn in barns_affected:
            if isinstance(barn, Barn):
                resources: List[str] = barn.get_resource_names()
                for resource in resources:
                    barn.remove_resource(resource, barn.get_resource(resource))
