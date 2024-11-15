from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.work.construction.construction import Construction

from src.settings import settings

class ConstructionFarm(Construction):
    def __init__(self, grid: Grid, location: Location):
        super().__init__(
            grid,
            location,
            settings.get("farm_size", 5),
            settings.get("farm_size", 5),
            settings.get("farm_construction_char", "f"),
            required_wood=settings.get("farm_req_wood", 30),
            required_stone=settings.get("farm_req_stone", 0),
            max_work_count=settings.get("farm_max_construction_work_count", 2),
            max_worker_count=settings.get("farm_max_construction_worker_count", 3),
            finished_completion_level=settings.get("farm_finished_completion_level", 3),
        )
