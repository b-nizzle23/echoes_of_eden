from typing import List, Set

from src.simulation.grid.location import Location


class Memory:
    def __init__(self) -> None:
        self.barns: Set[Location] = set()
        self.construction_barns: Set[Location] = set()
        self.farms: Set[Location] = set()
        self.construction_farms: Set[Location] = set()
        self.mines: Set[Location] = set()
        self.construction_mines: Set[Location] = set()
        self.homes: Set[Location] = set()
        self.construction_homes: Set[Location] = set()
        self.trees: Set[Location] = set()
        self.empties: Set[Location] = set()
        self.people: Set[Location] = set()
        self.items: List[str] = list(vars(self).keys())

    def dont_know_where_anything_is(self) -> bool:
        return not (self.barns or self.farms or self.homes or self.mines)

    def combine(self, other: "Memory") -> None:
        for item in self.items:
            for location in getattr(other, item):
                self.add(item, location)

    def add(self, what: str, where: Location) -> None:
        if what is None or where is None:
            return
        if what not in self.items:
            return
        for item in self.items:
            if item != what:
                self.__remove(item, where)
        getattr(self, what).add(where)

    def __remove(self, what: str, where: Location) -> None:
        if what is None or where is None:
            return
        if what not in self.items:
            return
        if where in getattr(self, what):
            getattr(self, what).remove(where)

    def __repr__(self) -> str:
        return str(
            {
                "barns": self.barns,
                "construction_barns": self.construction_barns,
                "farms": self.farms,
                "construction_farms": self.construction_farms,
                "mines": self.mines,
                "construction_mines": self.construction_mines,
                "homes": self.homes,
                "construction_homes": self.construction_homes,
                "trees": self.trees,
                "empties": self.empties,
                "people": self.people,
            }
        )
