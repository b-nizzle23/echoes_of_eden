from __future__ import annotations

from typing import TYPE_CHECKING

from src.settings import settings
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.scheduler.task.construction.build import \
    Build

if TYPE_CHECKING:
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class BuildMine(Build):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(
            simulation,
            person,
            settings.get("build_mine_priority", 5),
            StructureType.CONSTRUCTION_MINE,
            StructureType.BARN,
        )
