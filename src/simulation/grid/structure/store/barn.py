from __future__ import annotations

from typing import TYPE_CHECKING

from src.simulation.grid.structure.store.store import Store
from src.settings import settings

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location


class Barn(Store):
    def __init__(self, grid: Grid, location: Location) -> None:
        # Barn stores food, wood, and stone with specific capacities
        allowed_resources = {"food": settings.get("barn_food_store", 500),
                             "stone": settings.get("barn_stone_store", 100),
                             "wood": settings.get("barn_wood_store", 200)}
        super().__init__(grid,
                         location,
                         settings.get("barn_size", 3),
                         settings.get("barn_size", 3),
                         settings.get("barn_char", "B"),
                         allowed_resources)

