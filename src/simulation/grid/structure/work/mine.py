from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import numpy as np

from src.simulation.grid.structure.work.work import Work
from src.settings import settings
if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location


class Mine(Work):
    def __init__(self, grid: Grid, location: Location) -> None:
        max_worker_count: int = settings.get("mine_max_worker_count", 6)
        max_work_count: int = settings.get("mine_max_work_count", 4)
        yield_func: Callable[[], float] = lambda: np.random.normal(loc=settings.get("mine_yield_func_loc", 3),
                                                                   scale=settings.get("mine_yield_func_scale", 1)
                                                                   )
        yield_variance = np.random.normal(loc = settings.get("mine_yield_var_loc", 3),
                                          scale = settings.get("mine_yield_var_scale", 0.9)
                                          )
        super().__init__(grid,
                         location,
                         settings.get("mine_size", 3),
                         settings.get("mine_size", 3),
                         settings.get("mine_char", "M"),
                         max_worker_count,
                         max_work_count,
                         yield_func,
                         yield_variance)
