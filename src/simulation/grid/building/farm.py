from src.simulation.grid.building.building import Building


class Farm(Building):
    def __init__(self, grid, x, y) -> None:
        super().__init__(grid, x, y, 5, 5, "f", "F")
