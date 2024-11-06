from src.simulation.grid.building.building import Building


class Home(Building):
    def __init__(self, grid, x, y) -> None:
        super().__init__(grid, x, y, 2, 2, "h", "H")
