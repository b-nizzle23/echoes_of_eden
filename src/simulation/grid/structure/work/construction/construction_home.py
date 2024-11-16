from __future__ import annotations

from typing import TYPE_CHECKING

from src.simulation.grid.structure.work.construction.construction import Construction
from src.settings import settings
if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location


class ConstructionHome(Construction):
    def __init__(self, grid: Grid, location: Location):
        super().__init__(
            grid,
            location,
            settings.get("home_size", 2),
            settings.get("home_size", 2),
            settings.get("home_construction_char", "h"),
            required_wood=settings.get("home_req_wood", 20),
            required_stone=settings.get("home_req_stone", 10),
            max_work_count=settings.get("home_max_construction_work_count", 2),
            max_worker_count=settings.get("home_max_construction_worker_count", 2),
            finished_completion_level=settings.get("home_finished_completion_level", 3),
        )
