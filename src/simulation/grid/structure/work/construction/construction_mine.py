from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.work.construction.construction import Construction
from src.settings import settings  # Assuming settings is used to load the YAML file

class ConstructionMine(Construction):
    def __init__(self, grid: Grid, location: Location):
        super().__init__(
            grid,
            location,
            settings.get("mine_size", 3),
            settings.get("mine_size", 3),
            settings.get("mine_construction_char", "m"),
            required_wood=settings.get("mine_req_wood", 40),
            required_stone=settings.get("mine_req_stone", 40),
            max_work_count=settings.get("mine_max_construction_work_count", 5),
            max_worker_count=settings.get("mine_max_construction_worker_count", 3),
            finished_completion_level=settings.get("mine_finished_completion_level", 5),
        )
