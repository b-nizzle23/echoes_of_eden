from __future__ import annotations

from typing import TYPE_CHECKING

from src.simulation.grid.structure.work.construction.construction import Construction
from src.settings import settings
from src.logger import logger

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location


class ConstructionHome(Construction):
    def __init__(self, grid: Grid, location: Location):
        logger.debug(f"Initializing ConstructionHome at location {location}")

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

        logger.info(f"ConstructionHome initialized with required wood: {settings.get('home_req_wood', 20)}, "
                    f"required stone: {settings.get('home_req_stone', 10)}, "
                    f"max workers: {settings.get('home_max_construction_worker_count', 2)}, "
                    f"max work count: {settings.get('home_max_construction_work_count', 2)}, "
                    f"finished completion level: {settings.get('home_finished_completion_level', 3)}")
