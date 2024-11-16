from src.settings import settings
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.person import Person
from src.simulation.people.person.scheduler.task.work.work import Work
from src.simulation.simulation import Simulation


class WorkFarm(Work):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation,
                         person,
                         settings.get("work_farm_priority", 5),
                         StructureType.FARM,
                         settings.get("food", "food"))
