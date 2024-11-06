<<<<<<< Updated upstream:src/simulation/people/person/scheduler/task/task_factory.py
=======
from src.simulation.people.person.person import Person
from src.simulation.people.person._scheduler.task.task import Task
from src.simulation.people.person._scheduler.task.task_type import TaskType
from src.simulation.people.person._scheduler.task.eat import Eat
from src.simulation.people.person._scheduler.task.find_home import FindHome
from src.simulation.people.person._scheduler.task.find_spouse import FindSpouse
>>>>>>> Stashed changes:src/simulation/people/person/_scheduler/task/task_factory.py
from typing import Type

from src.simulation.people.person.person import Person
from eat import Eat
from find_home import FindHome
from find_spouse import FindSpouse
from task import Task
from task_type import TaskType
from src.simulation.simulation import Simulation


class TaskFactory:
    _constructors: dict[TaskType, Type] = {
        TaskType.EAT: Eat,
        TaskType.FIND_HOME: FindHome,
        TaskType.FIND_SPOUSE: FindSpouse,
        # TODO: add the rest of the tasks
    }

    def __init__(self, simulation: Simulation, person: Person) -> None:
        self._simulation = simulation
        self._person = person

    def create_instance(self, what: TaskType) -> Task:
        task_class: Type = self._constructors[what]
        return task_class(self._simulation, self._person)
