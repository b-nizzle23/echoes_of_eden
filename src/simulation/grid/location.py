from typing import List

from src.logger import logger
from src.settings import settings


class Location:
    def __init__(self, x: int, y: int) -> None:
        logger.debug(f"Initializing Location with x={x}, y={y}")
        self.x = x
        self.y = y
        
        self._neighbor_offsets = [
            (-1, -1),
            (0, -1),
            (1, -1),  # Top-left, Top, Top-right
            (-1, 0),
            (1, 0),  # Left,          Right
            (-1, 1),
            (0, 1),
            (1, 1),  # Bottom-left, Bottom, Bottom-right
        ]

    def __eq__(self, other) -> bool:
        logger.debug(f"Comparing Location({self.x}, {self.y}) to {other}")
        if not isinstance(other, Location):
            logger.debug("Other is not a Location instance, returning False.")
            return False
        result = self.x == other.x and self.y == other.y
        logger.debug(f"Equality result: {result}")
        return result

    def __hash__(self) -> int:
        logger.debug(f"Hashing Location({self.x}, {self.y})")
        return hash((self.x, self.y))

    def __copy__(self) -> "Location":
        logger.debug(f"Copying Location({self.x}, {self.y})")
        return Location(self.x, self.y)

    def __str__(self) -> str:
        location_str = f"Location(x={self.x}, y={self.y})"
        logger.debug(f"String representation: {location_str}")
        return location_str

    def distance_to(self, other: "Location") -> float:
        logger.debug(f"Calculating distance from Location({self.x}, {self.y}) to {other}")
        if not isinstance(other, Location):
            logger.error("Argument must be a Location instance")
            raise ValueError("Argument must be a Location instance")
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        logger.debug(f"Calculated distance: {distance}")
        return distance

    def is_one_away(self, other: "Location") -> bool:
        logger.debug(f"Checking if Location({self.x}, {self.y}) is one step away from {other}")
    
        # Check if the difference between the current location and the other location
        # matches any of the offsets in _neighbor_offsets
        for dx, dy in self._neighbor_offsets:
            if self.x + dx == other.x and self.y + dy == other.y:
                logger.debug(f"One step away: True")
                return True
    
        logger.debug(f"One step away: False")
        return False


    def get_neighbors(self) -> List["Location"]:
        logger.debug(f"Getting neighbors for Location({self.x}, {self.y})")
        
        neighbors = []
        for dx, dy in self._neighbor_offsets:
            new_location = Location(self.x + dx, self.y + dy)
            logger.debug(f"Adding neighbor: {new_location}")
            neighbors.append(new_location)

        logger.debug(f"Total neighbors found: {len(neighbors)}")
        return neighbors

    def is_near(self, location: "Location", distance: int = settings.get("near", 5)) -> bool:
        logger.debug(f"Checking if Location({self.x}, {self.y}) is near {location} within distance {distance}")
        result = self.distance_to(location) < distance
        logger.debug(f"Is near result: {result}")
        return result
