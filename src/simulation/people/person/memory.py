from typing import List, Set

from src.simulation.grid.location import Location


class Memory:
    def __init__(self) -> None:
        self._barns: Set[Location] = set()
        self._construction_barns: Set[Location] = set()
        self._farms: Set[Location] = set()
        self._construction_farms: Set[Location] = set()
        self._mines: Set[Location] = set()
        self._construction_mines: Set[Location] = set()
        self._homes: Set[Location] = set()
        self._construction_homes: Set[Location] = set()
        self._trees: Set[Location] = set()
        self._empties: Set[Location] = set()
        self._people: Set[Location] = set()
        self._items: List[str] = list(vars(self).keys())

    def get_barn_locations(self) -> Set[Location]:
        return self._barns

    def get_farm_locations(self) -> Set[Location]:
        return self._farms

    def get_mine_locations(self) -> Set[Location]:
        return self._mines

    def get_home_locations(self) -> Set[Location]:
        return self._homes

    def get_tree_locations(self) -> Set[Location]:
        return self._trees

    def get_empty_locations(self) -> Set[Location]:
        return self._empties

    def get_building_locations(self) -> Set[Location]:
        return self._barns | self._farms | self._mines | self._homes | self._trees

    def dont_know_where_anything_is(self) -> bool:
        return not (self._barns or self._farms or self._homes or self._mines)

    def combine(self, other: "Memory") -> None:
        for item in self._items:
            for location in getattr(other, item):
                self.add(item, location)

    # TODO: Add a param here for time to keep track of how old the person was
    #  when they added that thing to their memory
    def add(self, what: str, where: Location) -> None:
        if what is None or where is None:
            return
        if what not in self._items:
            return
        for item in self._items:
            if item != what:
                self._remove(item, where)
        getattr(self, what).add(where)

    def _remove(self, what: str, where: Location) -> None:
        if what is None or where is None:
            return
        if what not in self._items:
            return
        if where in getattr(self, what):
            getattr(self, what).remove(where)

    def __repr__(self) -> str:
        return str(
            {
                "barns": self._barns,
                "construction_barns": self._construction_barns,
                "farms": self._farms,
                "construction_farms": self._construction_farms,
                "mines": self._mines,
                "construction_mines": self._construction_mines,
                "homes": self._homes,
                "construction_homes": self._construction_homes,
                "trees": self._trees,
                "empties": self._empties,
                "people": self._people,
            }
        )

# TODO filter locations for building locations (top left corner)
