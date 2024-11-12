from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.store.store import Store


class Barn(Store):
    def __init__(self, grid: Grid, location: Location) -> None:
        # Barn stores food, wood, and stone with specific capacities
        allowed_resources = {"food": 500, "stone": 100, "wood": 200}
        super().__init__(grid, location, 3, 3, "B", allowed_resources)

