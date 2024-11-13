from typing import override

import numpy as np

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.work.work import Work


class Mine(Work):
    def __init__(self, grid: Grid, location: Location) -> None:
        max_worker_count = 6
        max_work_count = 4
        super().__init__(grid, location, 3, 3, "M", max_worker_count, max_work_count)


    @override
    def _get_yield(self) -> float:
        """
        Yield logic for the Mine class, with a mean of 4 and a standard deviation of 1.
        """
        return np.random.normal(loc=4, scale=1)
