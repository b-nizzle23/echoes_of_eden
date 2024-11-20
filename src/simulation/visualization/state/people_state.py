from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.people import People
from src.simulation.visualization.state.state import State


class PeopleState(State):
    def __init__(self, people: People):
        self._people: People = people

        logger.debug("Initializing people state.")

        self._people_count: int = len(people)
        self._average_health: float = self._get_average_health()
        self._average_hunger: float = self._get_average_hunger()

        logger.debug(f"Initialized with {self._people_count} people, average health: {self._average_health}, average hunger: {self._average_hunger}.")

        del self._people

    def _get_average_health(self) -> float:
        logger.debug("Calculating average health.")
        average_health: float = 0.0
        for person in self._people:
            person_health = person.get_health()
            logger.debug(f"Person {person} has health: {person_health}.")
            average_health += person_health
        if self._people:
            average_health /= len(self._people)
        logger.debug(f"Calculated average health: {average_health}.")
        return average_health

    def _get_average_hunger(self) -> float:
        logger.debug("Calculating average hunger.")
        average_hunger: float = 0.0
        for person in self._people:
            person_hunger = person.get_hunger()
            logger.debug(f"Person {person} has hunger: {person_hunger}.")
            average_hunger += person_hunger
        if self._people:
            average_hunger /= len(self._people)
        logger.debug(f"Calculated average hunger: {average_hunger}.")
        return average_hunger

