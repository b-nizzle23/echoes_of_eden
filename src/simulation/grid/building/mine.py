from src.simulation.grid.building.building import Building


class Mine(Building):
    def __init__(self, grid, x, y):
        super().__init__(grid, x, y, 3, 3, 'm', 'M')