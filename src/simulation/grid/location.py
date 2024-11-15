from typing import List


class Location:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def distance_to(self, other: "Location") -> float:
        if not isinstance(other, Location):
            raise ValueError("Argument must be a Location instance")
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def is_one_away(self, other: "Location") -> bool:
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1

    def get_neighbors(self) -> List["Location"]:
        # List of relative offsets for all 8 possible neighbors
        neighbor_offsets = [
            (-1, -1),
            (0, -1),
            (1, -1),  # Top-left, Top, Top-right
            (-1, 0),
            (1, 0),  # Left,          Right
            (-1, 1),
            (0, 1),
            (1, 1),  # Bottom-left, Bottom, Bottom-right
        ]

        neighbors = []
        for dx, dy in neighbor_offsets:
            neighbors.append(Location(self.x + dx, self.y + dy))

        return neighbors

    def is_near(self, location: "Location", distance: int = 5) -> bool:
        return self.distance_to(location) < distance

    def __copy__(self) -> "Location":
        return Location(self.x, self.y)

    def __str__(self) -> str:
        return f"Location(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return self.x == other.x and self.y == other.y
