from building import Building


class Barn(Building):
    def __init__(self, grid, x, y) -> None:
        super().__init__(grid, x, y, 3, 3, "b", "B")
