from typing import List, Set

from src.simulation.grid.location import Location
from src.simulation.people.person.person import Person

class Memory:
    def __init__(self, what: str, where: Location, when: int):
        self._what: str = what
        self._where: Location = where
        self._when: int = when
        
    def get_what(self) -> str:
        return self._what
    
    def get_where(self) -> Location:
        return self._where
    
    def get_when(self) -> int:
        return self._when

    def __hash__(self) -> int:
        return hash(self._where)

    def __eq__(self, other) -> bool:
        if isinstance(other, Memory):
            return self._where == other._where
        return False

class Memories:
    def __init__(self, person: Person) -> None:
        self._person: Person = person
        
        self._memories: Set[Memory] = set()
        
    def _get_locations(self, char: str) -> Set[Location]:
        return set(map(lambda memory: memory.get_where(), filter(lambda memory: memory.get_what() == char, self._memories)))

    def get_barn_locations(self) -> Set[Location]:
        return self._get_locations("B")

    def get_barn_construction_locations(self) -> Set[Location]:
        return self._get_locations("b")

    def get_farm_locations(self) -> Set[Location]:
        return self._get_locations("F")

    def get_farm_construction_locations(self) -> Set[Location]:
        return self._get_locations("f")

    def get_mine_locations(self) -> Set[Location]:
        return self._get_locations("M")

    def get_mine_construction_locations(self) -> Set[Location]:
        return self._get_locations("m")

    def get_home_locations(self) -> Set[Location]:
        return self._get_locations("H")

    def get_home_construction_locations(self) -> Set[Location]:
        return self._get_locations("h")

    def get_tree_locations(self) -> Set[Location]:
        return self._get_locations("*")

    def get_empty_locations(self) -> Set[Location]:
        return self._get_locations(" ")

    def get_building_locations(self) -> Set[Location]:
        return self.get_barn_locations() | self.get_farm_locations() | self.get_mine_locations() | self.get_home_locations()

    # TODO finish this
    def combine(self, other: "Memories") -> None:
        pass

    # TODO: Add a param here for time to keep track of how old the person was
    #  when they added that thing to their memory
    # TODO filter locations for building locations (top left corner)
    def add(self, what: str, where: Location) -> None:
        pass

    def _remove(self, what: str, where: Location) -> None:
        pass
