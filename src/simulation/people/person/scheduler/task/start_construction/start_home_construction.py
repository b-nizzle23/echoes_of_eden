from src.settings import settings
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.person import Person
from src.simulation.people.person.scheduler.task.start_construction.start_construction import (
    StartConstruction,
)
from src.simulation.simulation import Simulation


class StartHomeConstruction(StartConstruction):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation,
                         person,
                         settings.get("start_home_priority", 5),
                         settings.get("home_size", 2),
                         settings.get("home_size", 2),
                         StructureType.CONSTRUCTION_HOME)
