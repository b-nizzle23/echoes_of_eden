from src.simulation.grid.location import Location
from src.simulation.people.person.person import Person
import random
from typing import List

from src.simulation.simulation import Simulation


class PeopleGenerator:
    def __init__(self, simulation: Simulation, num_people: int = 20) -> None:
        self._max_pk: int = num_people
        self._simulation: Simulation = simulation
        self._names: List[str] = self._get_names()

    @staticmethod
    def _get_names() -> List[str]:
        with open("../../../../data/first_names.txt", "r") as file:
            names: List[str] = [line.strip() for line in file if line.strip()]
        return names

    def generate(self) -> List[Person]:
        people: List[Person] = []
        for pk in range(self._max_pk):
            name: str = random.choice(self._names)
            location: Location = Location(
                20, 20
            )  # TODO place them in different valid spots near the town
            age: int = random.randint(20, 30)
            person: Person = Person(self._simulation, name, pk, location, age)
            people.append(person)
        return people
