from typing import Callable

import numpy as np

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.work.work import Work


class Tree(Work):
    def __init__(self, grid: Grid, location: Location) -> None:
        max_worker_count: int = 1
        max_work_count: int = 2
        yield_func: Callable[[], float] = lambda: np.random.normal(loc=3, scale=1)
        super().__init__(grid, location, 1, 1, "*", max_worker_count, max_work_count, yield_func)

    def __del__(self):
        self._grid.remove_tree(self._location)
