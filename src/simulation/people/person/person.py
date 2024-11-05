from simulation.people.person.memory import Memory
from simulation.people.person.mover import Mover
from simulation.people.person.scheduler.scheduler import Scheduler
from simulation.people.person.scheduler.task.task_type import TaskType


class Person:
    def __init__(self, simulation, name, pk, location, age):
        self._name = name
        self._pk = pk
        self._age = age

        # where the person is located
        # (x, y)
        self._location = location

        self._memory = Memory()

        self._mover = Mover(simulation.get_grid(), self, self._memory, 10)

        self._health: int = 100
        self._hunger: int = (
            100  # when your hunger gets below 25, health starts going down; when it gets above 75, health starts going up
        )
        self._home = None
        self._spouse = None
        self._scheduler = Scheduler(simulation, self)

    def take_action(self):
        self._hunger -= 1  # TODO adjust

        if self._hunger < 20:
            self._health -= 1
        elif self._hunger > 80:
            self._health += 1

        if not self._home:
            self._scheduler.add(TaskType.FIND_HOME)

        if not self._spouse:
            self._scheduler.add(TaskType.FIND_SPOUSE)
        else:
            # TODO chance to have a baby
            pass

        if self._hunger < 50:
            self._scheduler.add(TaskType.EAT)

        self._scheduler.execute()

    def get_location(self):
        return self._location

    def set_location(self, other):
        # TODO check if its in bounds
        self._location = other

    def is_dead(self):
        return self._health <= 0 or self._age >= 80

    def eat(self):
        self._hunger += 10

    def assign_spouse(self, spouse):
        self._spouse = spouse

    def assign_home(self, home):
        self._home = home

    def age(self):
        self._age += 1

    def is_home(self):
        pass

    def go_to_home(self):
        pass

    def find_farm_to_work_at(self):
        pass

    def find_mine_to_work_at(self):
        pass

    def find_barn_to_store_at(self):
        pass

    def __str__(self):
        pass  # TODO implement what to print for a person
