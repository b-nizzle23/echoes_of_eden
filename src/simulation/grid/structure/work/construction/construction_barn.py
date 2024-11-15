from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.work.construction.construction import Construction

from src.settings import settings

class ConstructionBarn(Construction):
    def __init__(self, grid: Grid, location: Location):
        super().__init__(
            grid,
            location,
            settings.get("barn_size", 3),
            settings.get("barn_size", 3),
            settings.get("barn_construction_char", "b"),
            required_wood=settings.get("barn_req_wood", 60),
            required_stone=settings.get("barn_req_stone", 30),
            max_work_count=settings.get("barn_max_construction_work_count", 3),
            max_worker_count=settings.get("barn_max_construction_worker_count", 3),
            finished_completion_level=settings.get("barn_finished_completion_level", 5),
        )
