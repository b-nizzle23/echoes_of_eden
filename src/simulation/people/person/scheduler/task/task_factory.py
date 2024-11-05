from simulation.people.person.scheduler.task.task_type import TaskType
from simulation.people.person.scheduler.task.eat import Eat
from simulation.people.person.scheduler.task.find_home import FindHome
from simulation.people.person.scheduler.task.find_spouse import FindSpouse


class TaskFactory:
    _constructors = {
        TaskType.EAT: Eat,
        TaskType.FIND_HOME: FindHome,
        TaskType.FIND_SPOUSE: FindSpouse,
        # TODO add the rest of the tasks
    }

    def __init__(self, simulation, person):
        self._simulation = simulation
        self._person = person

    def create_instance(self, what):
        return self._constructors[what](self._simulation, self._person)
