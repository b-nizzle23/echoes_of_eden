from typing import List, Iterator, Dict

from people_generator import PeopleGenerator
from person.person import Person
from .home_manager import HomeManager
from ..grid.grid import Grid

from ..simulation import Simulation
from .people_disaster_generator import PeopleDisasterGenerator


class People:
    def __init__(self, simulation: "Simulation", actions_per_day: int) -> None:
        self._simulation = simulation
        self._grid: Grid = simulation.get_grid()
        self._actions_per_day: int = actions_per_day
        self._people_generator: PeopleGenerator = PeopleGenerator(simulation)
        self._people: List[Person] = self._people_generator.generate()
        self._disaster_generator: PeopleDisasterGenerator = PeopleDisasterGenerator(
            self
        )
        self._home_manager: HomeManager = HomeManager(self)

    def take_actions_for_day(self) -> None:
        for action in range(self._actions_per_day):
            self._simulation.increment_time()
            dead: List[Person] = []
            for person in self._people:
                if person.is_dead():
                    dead.append(person)
                    continue
                person.take_action()
                self._grid.work_structures_exchange_memories()
            for person in dead:
                person.divorce()
                self._people.remove(person)

    def swap_homes(self) -> None:
        self._home_manager.swap_homes()

    def kill_stuck(self) -> None:
        for person in self._people:
            if person.is_stuck():
                person.kill()  # they got stuck and died

    def spouses_share_memory(self):
        for person in self.get_married_people():
            person.exchange_memories(person.get_spouse())

    def get_time(self) -> int:
        return self._simulation.get_time()
    
    def get_people(self) -> List:
        return self._people
        
    def flush(self):
        self._disaster_generator.flush()
        for person in self._people:
            person.get_scheduler().flush()

    def generate_disasters(self, chance: float = 0.50) -> None:
        self._disaster_generator.generate(chance)

    def print(self) -> None:
        for person in self._people:
            print(person)

    def age(self) -> None:
        for person in self._people:
            person.age()

    def __len__(self) -> int:
        return len(self._people)

    def get_average_health(self) -> float:
        average_health: float = 0.0
        for person in self._people:
            average_health += person.get_health()
        average_health /= len(self._people)
        return average_health

    def get_average_hunger(self) -> float:
        average_hunger: float = 0.0
        for person in self._people:
            average_hunger += person.get_hunger()
        average_hunger /= len(self._people)
        return average_hunger

    def make_babies(self) -> None:
        for person in self.get_married_people():
            if (
                (person.get_age() >= 18)
                and (person.get_age() <= 50)
                and (person.get_spouse().get_age() >= 18)
                and (person.get_spouse().get_age() <= 50)
            ):
                # create a baby next to the person's house
                baby = self._people_generator.make_baby(
                    person.get_home().get_location()
                )
                self._people.append(baby)

    def get_married_people(self) -> List[Person]:
        married_people: List[Person] = []
        visited_people: List[Person] = []
        for person in self._people:
            if person in visited_people:
                continue
            if not person.has_spouse():
                visited_people.append(person)
                continue
            visited_people.append(person)
            visited_people.append(person.get_spouse())
            if not person.has_home():
                continue
            married_people.append(person)
        return married_people
    
    def get_disaster_counts(self) -> Dict[str, int]:
        return self._disaster_generator.get_disaster_counts()

    def __iter__(self) -> Iterator["Person"]:
        return iter(self._people)
