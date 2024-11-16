from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Type

from src.simulation.people.person.scheduler.task.construction.build_barn import BuildBarn
from src.simulation.people.person.scheduler.task.construction.build_farm import BuildFarm
from src.simulation.people.person.scheduler.task.construction.build_home import BuildHome
from src.simulation.people.person.scheduler.task.construction.build_mine import BuildMine
from src.simulation.people.person.scheduler.task.eat import Eat
from src.simulation.people.person.scheduler.task.explore import Explore
from src.simulation.people.person.scheduler.task.find_home import FindHome
from src.simulation.people.person.scheduler.task.find_spouse import FindSpouse
from src.simulation.people.person.scheduler.task.start_construction.start_barn_construction import StartBarnConstruction
from src.simulation.people.person.scheduler.task.start_construction.start_farm_construction import StartFarmConstruction
from src.simulation.people.person.scheduler.task.start_construction.start_home_construction import StartHomeConstruction
from src.simulation.people.person.scheduler.task.start_construction.start_mine_construction import StartMineConstruction
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.simulation.people.person.scheduler.task.transport import Transport
from src.simulation.people.person.scheduler.task.work.chop_tree import ChopTree
from src.simulation.people.person.scheduler.task.work.work_farm import WorkFarm
from src.simulation.people.person.scheduler.task.work.work_mine import WorkMine

if TYPE_CHECKING:
    from src.simulation.simulation import Simulation
    from src.simulation.people.person.person import Person
    from src.simulation.people.person.scheduler.task.task import Task


class TaskFactory:
    _constructors: Dict[TaskType, Type] = {
        TaskType.EAT: Eat,
        TaskType.FIND_HOME: FindHome,
        TaskType.FIND_SPOUSE: FindSpouse,
        TaskType.WORK_FARM: WorkFarm,
        TaskType.WORK_MINE: WorkMine,
        TaskType.CHOP_TREE: ChopTree,
        TaskType.BUILD_HOME: BuildHome,
        TaskType.BUILD_FARM: BuildFarm,
        TaskType.BUILD_MINE: BuildMine,
        TaskType.BUILD_BARN: BuildBarn,
        TaskType.EXPLORE: Explore,
        TaskType.START_FARM_CONSTRUCTION: StartFarmConstruction,
        TaskType.START_MINE_CONSTRUCTION: StartMineConstruction,
        TaskType.START_HOME_CONSTRUCTION: StartHomeConstruction,
        TaskType.START_BARN_CONSTRUCTION: StartBarnConstruction,
        TaskType.TRANSPORT: Transport,
    }

    def __init__(self, simulation: Simulation, person: Person) -> None:
        self._simulation = simulation
        self._person = person

    def create_instance(self, what: TaskType) -> Optional[Task]:
        task_class: Type = self._constructors[what]
        if not task_class:
            return None
        return task_class(self._simulation, self._person, what)
