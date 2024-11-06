from src.simulation.people.person.person import Person
<<<<<<< Updated upstream:src/simulation/people/person/scheduler/task/eat.py
from task import Task
=======
from src.simulation.people.person._scheduler.task.task import Task
>>>>>>> Stashed changes:src/simulation/people/person/_scheduler/task/eat.py
from src.simulation.simulation import Simulation


class Eat(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation, person, 10)

    def execute(self) -> None:
        if not self._person.is_home():
            self._person.go_to_home()
        else:
            self._person.eat()
            self._finished()
