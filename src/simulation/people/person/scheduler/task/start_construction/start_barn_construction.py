from __future__ import annotations

from typing import TYPE_CHECKING

from src.settings import settings
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.scheduler.task.start_construction.start_construction import StartConstruction

if TYPE_CHECKING:
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class StartBarnConstruction(StartConstruction):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation,
                         person,
                         settings.get("start_barn_priority", 5),
                         settings.get("barn_size", 3),
                         settings.get("barn_size", 3),
                         StructureType.CONSTRUCTION_BARN)
