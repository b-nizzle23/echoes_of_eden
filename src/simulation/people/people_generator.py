from __future__ import annotations

import random
from copy import deepcopy
from typing import TYPE_CHECKING, List

from src.logger import logger
from src.settings import settings
from src.simulation.grid.structure.store.home import Home
from src.simulation.people.person.person import Person

if TYPE_CHECKING:
    from src.simulation.simulation import Simulation
    from src.simulation.grid.location import Location


class PeopleGenerator:
    def __init__(self, simulation: Simulation) -> None:
        self._grid = simulation.get_grid()
        home_count: int = self._grid.get_structure_count(Home)
        # Randomly assign 1 or 2 people per home, then calculate the total number of people
        total_people = sum(random.choice([1, 2]) for _ in range(home_count))
        self._max_pk = total_people
        self._simulation: Simulation = simulation

    @staticmethod
    def _get_names() -> List[str]:
        try:
            with open("../../../data/first_names.txt", "r") as file:
                names: List[str] = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            logger.error("Could not find names file. Using default names.")
            names: List[str] = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Joseph', 'Charles', 'Thomas', 'Daniel',
                   'Emma', 'Olivia', 'Sophia', 'Isabella', 'Ava', 'Mia', 'Amelia', 'Harper', 'Evelyn', 'Abigail']
        return names

    def generate(self) -> List[Person]:
        people: List[Person] = []
        names: List[str] = self._get_names()
        empty_spots_near_town: List[Location] = self._grid.get_empty_spots_near_town()
        for pk in range(self._max_pk):
            name: str = random.choice(names)
            location: Location = deepcopy(random.choice(empty_spots_near_town))
            age: int = random.randint(
                settings.get("inital_spawn_age_min", 20),
                settings.get("inital_spawn_age_max", 30))
            person: Person = Person(self._simulation, name, pk, location, age)
            people.append(person)
        return people

    def make_baby(self, location: Location) -> Person:
        name: str = random.choice(self._get_names())
        age: int = 0
        self._max_pk += 1
        person: Person = Person(self._simulation, name, self._max_pk, location, age)
        return person
