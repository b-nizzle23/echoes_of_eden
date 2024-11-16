from typing import List

from src.settings import settings
from src.simulation.grid.grid import Grid
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.visualization.state.state import State


class ResourceState(State):
    def __init__(self, grid: Grid):
        self._barns: List[Barn] = []
        for barn in grid.get_structures(Barn):
            if isinstance(barn, Barn):
                self._barns.append(barn)
        self._total_food: int = self._get_total_food()
        self._total_stone: int = self._get_total_stone()
        self._total_wood: int = self._get_total_wood()
        self._total_capacity: int = self._get_total_barn_capacity()
        self._total_remaining_capacity: int = self._get_total_remaining_capacity()

    def _get_total_food(self) -> int:
        total_food = 0
        for barn in self._barns:
            total_food += barn.get_resource(settings.get("food", "food"))
        return total_food

    def _get_total_stone(self) -> int:
        total_stone = 0
        for barn in self._barns:
            total_stone += barn.get_resource(settings.get("stone", "stone"))
        return total_stone

    def _get_total_wood(self) -> int:
        total_wood = 0
        for barn in self._barns:
            total_wood += barn.get_resource(settings.get("wood", "wood"))
        return total_wood

    def _get_total_barn_capacity(self) -> int:
        total_capacity = 0
        for barn in self._barns:
            total_capacity += barn.get_capacity()
        return total_capacity

    def _get_total_remaining_capacity(self) -> int:
        total_remaining_capacity = 0
        # Calculate the remaining capacity for each barn
        for barn in self._barns:
            remaining_capacity = barn.get_remaining_capacity()
            total_remaining_capacity += remaining_capacity

        return total_remaining_capacity
