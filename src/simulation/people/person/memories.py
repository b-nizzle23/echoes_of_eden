from typing import Set

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location

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
    def __init__(self, grid: Grid) -> None:
        self._grid: Grid = grid
        
        self._memories: Set[Memory] = set()
        
    def get_memories(self) -> Set[Memory]:
        return self._memories
        
    def _get_locations(self, char: str) -> Set[Location]:
        current_time = self._grid.get_time()

        # Remove expired memories
        self._memories = {memory for memory in self._memories if current_time - memory.get_when() <= 50}
    
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

    def combine(self, other: "Memories") -> None:
        # Merge the memories from both 'self' and 'other', keeping the newest memory for each location
        for memory in other.get_memories():
            existing_memory = next((m for m in self._memories if m.get_where() == memory.get_where()), None)
            if existing_memory:
                # If an existing memory is found for the same location, compare the timestamps
                if memory.get_when() > existing_memory.get_when():
                    # Replace the old memory with the newer one
                    self.add(memory.get_what(), memory.get_where())
            else:
                # If no memory exists for this location, simply add the new memory
                self._memories.add(memory)

    def add(self, what: str, where: Location) -> None:
        if not self._grid.is_tree(where) or not self._grid.is_empty(where):
            self._grid.find_top_left_corner(where)

        # Remove any existing memory for the same location
        self._remove(where)
        # Create a new memory and add it to the set
        new_memory = Memory(what, where, self._grid.get_time())
        self._memories.add(new_memory)

    def _remove(self, where: Location) -> None:
        # Remove memory at the specified location if it exists
        self._memories = {memory for memory in self._memories if memory.get_where() != where}
