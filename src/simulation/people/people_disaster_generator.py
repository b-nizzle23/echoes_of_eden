import random

from src.simulation.people.people import People
from src.simulation.grid.location import Location
from src.simulation.people.person.scheduler.scheduler import Scheduler



class PeopleDisasterGenerator:
    def __init__(self, people: People):
        self._people = people
    
    def get_people(self) -> People:
        return self._people

    def generate(self, chance: float) -> None:
        """Randomly trigger one of several disasters with a given chance."""
        if random.random() < chance:

            # List of disaster methods
            disaster_methods = [
                self._divorce,
                self._sickness,
                self._craving,
                self._death,
                self._forget_tasks,
                self._sleepwalk,
                self._so_many_babies,
            ]

            # Randomly pick number of disasters to trigger, along with random severities
            disaster_count = random.ranint(1, len(disaster_methods) // 2)
            for _ in range(disaster_count):
                severity = random.randint(1, 10)  # Severity between 1 and 10
                chosen_disaster = random.choice(disaster_methods)
                chosen_disaster(severity)  # Call the chosen disaster method with severity

    def _divorce(self, severity: int) -> None:
        """Divorce event, causing relationship breakdown."""
        percent_affected = severity * 5 / 100
        married_list = [person for person in self.get_people().get_people_list() if person.get_spouse()]
        # Calculate the number of people to affect
        num_affected = int(len(married_list) * percent_affected)
        # Randomly select the individuals to be affected by divorce
        affected_people = random.sample(married_list, num_affected)
        visited = set()

        for person in affected_people:
            if person not in visited:
                spouse = person.get_spouse()
                person.divorce()
                visited.append(person)
                visited.append(spouse)

    def _sickness(self, severity: int) -> None:
        """Person gets sick, losing health."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            person.set_health(-30) # arbitrary decrement value

    def _craving(self, severity: int) -> None:
        """Craving causes hunger to increase."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            person.set_hunger(-30) # arbitrary decrement value

    def _death(self, severity: int) -> None:
        """A person dies."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            person.set_health(-101) # person is dead

    def _forget_tasks(self, severity: int) -> None:
        """Person forgets their tasks."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            person = Scheduler(person.get_simulation(), person)
            person.flush()

    def _sleepwalk(self, severity: int) -> None:
        """A person sleepwalks into the woods."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            # send person to a random corner of the grid.
            person.set_location(Location(0, 0))

    def _so_many_babies(self, severity: int) -> None:
        """A person or group has a baby boom."""
        people = self.get_people()
        if severity > 5:
            people.make_babies() # triplets
        people.make_babies() # twins         

    def _get_affected_people(self, severity: int, percent: float) -> People:
        percent_affected = severity * percent
        person_list = random.shuffle(self.get_people().get_people_list())
        num_affected = int(len(person_list) * percent_affected)
        return random.sample(person_list, num_affected)