from simulation.people.person.person import Person
import random


class PeopleGenerator:
    def __init__(self, simulation, num_people=20):
        self._max_pk = num_people
        self._simulation = simulation
        self._names = self._get_names()

    @staticmethod
    def _get_names():
        with open("../../../../data/first_names.txt", "r") as file:
            names = [line.strip() for line in file if line.strip()]
        return names

    def generate(self):
        people = []
        for pk in range(self._max_pk):
            name = random.choice(self._names)
            location = (
                20,
                20,
            )  # TODO place them in different valid spots near the town
            age = random.randint(20, 30)
            person = Person(self._simulation, name, pk, location, age)
            people.append(person)
        return people
