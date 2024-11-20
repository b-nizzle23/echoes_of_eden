from typing import Set

from src.settings import settings
from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.logger import logger

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
        logger.debug(f"Fetching locations associated with character '{char}'.")

        current_time = self._grid.get_time()
        logger.debug(f"Current simulation time is {current_time}.")

        # Remove expired memories
        expired_count = len(self._memories)
        self._memories = {
            memory for memory in self._memories if current_time - memory.get_when() <= settings.get("memory_expire", 50)
        }
        expired_count -= len(self._memories)
        if expired_count > 0:
            logger.debug(f"{expired_count} expired memories removed based on the expiration time.")

        filtered_memories = filter(lambda memory: memory.get_what() == char, self._memories)
        locations = set(map(lambda memory: memory.get_where(), filtered_memories))
        logger.debug(f"Found {len(locations)} locations associated with character '{char}'.")

        return locations

    def get_barn_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("barn_char", "B"))

    def get_barn_construction_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("barn_construction_char", "b"))

    def get_farm_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("farm_char", "F"))

    def get_farm_construction_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("farm_construction_char", "f"))

    def get_mine_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("mine_char", "M"))

    def get_mine_construction_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("mine_construction_char", "m"))

    def get_home_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("home_char", "H"))

    def get_home_construction_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("home_construction_char", "h"))

    def get_tree_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("tree_char", "*"))

    def get_empty_locations(self) -> Set[Location]:
        return self._get_locations(settings.get("empty_char", " "))

    def get_building_locations(self) -> Set[Location]:
        return (
            self.get_barn_locations()
            | self.get_farm_locations()
            | self.get_mine_locations()
            | self.get_home_locations()
        )

    def combine(self, other: "Memories") -> None:
        logger.debug("Combining memories from another instance into the current one.")

        other_memories_count = len(other.get_memories())
        logger.debug(f"The other memory instance contains {other_memories_count} memories.")

        # Merge the memories from both 'self' and 'other', keeping the newest memory for each location
        for memory in other.get_memories():
            existing_memory = next((m for m in self._memories if m.get_where() == memory.get_where()), None)
            if existing_memory:
                # If an existing memory is found for the same location, compare the timestamps
                logger.debug(
                    f"Memory conflict detected for location {memory.get_where()}. "
                    f"Existing memory timestamp: {existing_memory.get_when()}, "
                    f"incoming memory timestamp: {memory.get_when()}."
                )
                if memory.get_when() > existing_memory.get_when():
                    # Replace the old memory with the newer one
                    logger.debug(f"Incoming memory for location {memory.get_where()} is newer. Updating memory.")
                    self.add(memory.get_what(), memory.get_where())
                else:
                    logger.debug(f"Existing memory for location {memory.get_where()} is newer. No update needed.")
            else:
                # If no memory exists for this location, simply add the new memory
                logger.debug(f"No existing memory found for location {memory.get_where()}. Adding new memory.")
                self._memories.add(memory)

        logger.debug(f"Memory combination complete. Total memories after combination: {len(self._memories)}.")

    def add(self, what: str, where: Location) -> None:
        logger.debug(f"Adding a new memory with content '{what}' at location {where}.")

        # Validate location and adjust if necessary
        if not self._grid.is_tree(where) or not self._grid.is_empty(where):
            logger.debug(f"Location {where} is either not a tree or not empty. Adjusting location to top-left corner.")
            self._grid.find_top_left_corner(where)

        # Remove any existing memory for the same location
        logger.debug(f"Removing any existing memory at location {where}.")
        self._remove(where)

        # Create a new memory and add it to the set
        current_time = self._grid.get_time()
        new_memory = Memory(what, where, current_time)
        self._memories.add(new_memory)
        logger.debug(f"New memory added: '{what}' at location {where} with timestamp {current_time}.")
        logger.debug(f"Memory successfully added. Total memories: {len(self._memories)}.")

    def _remove(self, where: Location) -> None:
        logger.debug(f"Attempting to remove memory at location {where}.")

        # Count memories before removal
        initial_count = len(self._memories)
        logger.debug(f"Initial memory count: {initial_count}.")

        # Remove memory at the specified location if it exists
        self._memories = {memory for memory in self._memories if memory.get_where() != where}

        # Count memories after removal
        final_count = len(self._memories)
        logger.debug(f"Final memory count after removal: {final_count}.")

        # Log the result of the removal operation
        if final_count < initial_count:
            logger.debug(f"Memory at location {where} was successfully removed.")
        else:
            logger.debug(f"No memory found at location {where} to remove.")
