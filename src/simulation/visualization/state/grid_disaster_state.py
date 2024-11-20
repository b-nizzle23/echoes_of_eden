from typing import Dict

from src.simulation.grid.grid import Grid
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.visualization.state.state import State


class GridDisasterState(State):
    def __init__(self, grid: Grid):
        # Get disaster counts from the GridDisasterGenerator
        disaster_counts: Dict[str, int] = grid.get_disaster_counts()

        # Initialize disaster attributes based on counts
        self._rats_eat_home_food = disaster_counts.get("rats_eat_home_food", 0)
        logger.debug(f"Rats eat home food count: {self._rats_eat_home_food}")

        self._burn_buildings = disaster_counts.get("burn_buildings", 0)
        logger.debug(f"Burn buildings count: {self._burn_buildings}")

        self._decrease_farm_yield = disaster_counts.get("decrease_farm_yield", 0)
        logger.debug(f"Decrease farm yield count: {self._decrease_farm_yield}")

        self._decrease_mine_yield = disaster_counts.get("decrease_mine_yield", 0)
        logger.debug(f"Decrease mine yield count: {self._decrease_mine_yield}")

        self._forest_fire = disaster_counts.get("forest_fire", 0)
        logger.debug(f"Forest fire count: {self._forest_fire}")

        self._steal_barn_resources = disaster_counts.get("steal_barn_resources", 0)
        logger.debug(f"Steal barn resources count: {self._steal_barn_resources}")
