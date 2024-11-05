from simulation.people.person.scheduler.task.task import Task


class Eat(Task):
    def __init__(self, simulation, person):
        super().__init__(simulation, person, 10)

    def execute(self):
        if not self._person.is_home():
            self._person.go_to_home()
        else:
            self._person.eat()
            self._finished()
