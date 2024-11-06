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

    def __copy__(self) -> "Location":
        return Location(self.x, self.y)

    def __str__(self) -> str:
        return f"Location(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return self.x == other.x and self.y == other.y
