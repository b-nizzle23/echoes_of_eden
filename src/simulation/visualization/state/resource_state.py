from typing import List

from src.settings import settings
from src.simulation.grid.grid import Grid
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.visualization.state.state import State


class ResourceState(State):
    def __init__(self, grid: Grid):
        logger.debug("Initializing YourClassName with grid.")
        self._barns: List[Barn] = []

        for barn in grid.get_structures(Barn):
            if isinstance(barn, Barn):
                self._barns.append(barn)
                logger.debug(f"Added barn: {barn}")

        self._total_food: int = self._get_total_food()
        logger.debug(f"Total food: {self._total_food}")

        self._total_stone: int = self._get_total_stone()
        logger.debug(f"Total stone: {self._total_stone}")

        self._total_wood: int = self._get_total_wood()
        logger.debug(f"Total wood: {self._total_wood}")

        self._total_capacity: int = self._get_total_barn_capacity()
        logger.debug(f"Total barn capacity: {self._total_capacity}")

        self._total_remaining_capacity: int = self._get_total_remaining_capacity()
        logger.debug(f"Total remaining capacity: {self._total_remaining_capacity}")

    def _get_total_food(self) -> int:
        logger.debug("Calculating total food.")
        total_food = 0
        for barn in self._barns:
            food = barn.get_resource(settings.get("food", "food"))
            total_food += food
            logger.debug(f"Barn {barn} has {food} food.")
        logger.debug(f"Total food: {total_food}")
        return total_food

    def _get_total_stone(self) -> int:
        logger.debug("Calculating total stone.")
        total_stone = 0
        for barn in self._barns:
            stone = barn.get_resource(settings.get("stone", "stone"))
            total_stone += stone
            logger.debug(f"Barn {barn} has {stone} stone.")
        logger.debug(f"Total stone: {total_stone}")
        return total_stone

    def _get_total_wood(self) -> int:
        logger.debug("Calculating total wood.")
        total_wood = 0
        for barn in self._barns:
            wood = barn.get_resource(settings.get("wood", "wood"))
            total_wood += wood
            logger.debug(f"Barn {barn} has {wood} wood.")
        logger.debug(f"Total wood: {total_wood}")
        return total_wood

    def _get_total_barn_capacity(self) -> int:
        logger.debug("Calculating total barn capacity.")
        total_capacity = 0
        for barn in self._barns:
            capacity = barn.get_capacity()
            total_capacity += capacity
            logger.debug(f"Barn {barn} has capacity {capacity}.")
        logger.debug(f"Total barn capacity: {total_capacity}")
        return total_capacity

    def _get_total_remaining_capacity(self) -> int:
        logger.debug("Calculating total remaining barn capacity.")
        total_remaining_capacity = 0
        # Calculate the remaining capacity for each barn
        for barn in self._barns:
            remaining_capacity = barn.get_remaining_capacity()
            total_remaining_capacity += remaining_capacity
            logger.debug(f"Barn {barn} has remaining capacity: {remaining_capacity}.")

        logger.debug(f"Total remaining capacity: {total_remaining_capacity}")
        return total_remaining_capacity
