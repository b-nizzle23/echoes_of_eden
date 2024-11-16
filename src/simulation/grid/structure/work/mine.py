from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import numpy as np

from src.simulation.grid.structure.work.work import Work

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location


class Mine(Work):
    def __init__(self, grid: Grid, location: Location) -> None:
        max_worker_count: int = 6
        max_work_count: int = 4
        yield_func: Callable[[], float] = lambda: np.random.normal(loc=4, scale=1)
        yield_variance = np.random.normal(loc = 3, scale = 0.9)
        super().__init__(grid, location, 3, 3, "M", max_worker_count, max_work_count, yield_func, yield_variance)
