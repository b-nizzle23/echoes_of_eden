import random
from typing import Dict

from src.settings import settings
from src.simulation.people.people import People
from src.simulation.grid.location import Location
from src.simulation.people.person.scheduler.scheduler import Scheduler


class PeopleDisasterGenerator:
    def __init__(self, people: People):
        self._people = people
        # Initialize counters for each disaster type
        self._disaster_counts: Dict[str, int] = {
            'divorce': 0,
            'sickness': 0,
            'craving': 0,
            'death': 0,
            'forget_tasks': 0,
            'sleepwalk': 0,
            'so_many_babies': 0
        }

    def generate(self, chance: float) -> None:
        """Randomly trigger one of several disasters with a given chance."""
        if random.random() < chance:

            # List of disaster methods with their names
            disaster_methods = [
                (self._divorce, 'divorce'),
                (self._sickness, 'sickness'),
                (self._craving, 'craving'),
                (self._death, 'death'),
                (self._forget_tasks, 'forget_tasks'),
                (self._sleepwalk, 'sleepwalk'),
                (self._so_many_babies, 'so_many_babies'),
            ]

            # Randomly pick number of disasters to trigger, along with random severities
            disaster_count = random.randint(1, len(disaster_methods) // 2)
            for _ in range(disaster_count):
                severity = random.randint(1, 10)  # Severity between 1 and 10
                chosen_disaster, disaster_name = random.choice(disaster_methods)
                chosen_disaster(severity)  # Call the chosen disaster method with severity

                # Increment the disaster count for the chosen disaster
                self._disaster_counts[disaster_name] += 1

    def get_disaster_counts(self) -> Dict[str, int]:
        """Return the current disaster count statistics."""
        return self._disaster_counts
    
    def flush(self):
        """Reset all disaster counters to 0."""
        for disaster in self._disaster_counts:
            self._disaster_counts[disaster] = 0

    def _divorce(self, severity: int) -> None:
        """Divorce event, causing relationship breakdown."""
        percent_affected = severity * 5 / 100
        married_list = [person for person in self._people if person.get_spouse()]
        # Calculate the number of people to affect
        num_affected = int(len(married_list) * percent_affected)
        # Randomly select the individuals to be affected by divorce
        affected_people = random.sample(married_list, num_affected)
        visited = set()

        for person in affected_people:
            if person not in visited:
                spouse = person.get_spouse()
                person.divorce()
                visited.add(person)
                visited.add(spouse)

    def _sickness(self, severity: int) -> None:
        """Person gets sick, losing health."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            person.set_health(settings.get("sick_health_decr", -30)) # arbitrary decrement value

    def _craving(self, severity: int) -> None:
        """Craving causes hunger to increase."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            person.set_hunger(settings.get("sick_hunger_decr", -30)) # arbitrary decrement value

    def _death(self, severity: int) -> None:
        """A person dies."""
        affected_people = self._get_affected_people(severity, 0.1)
        for person in affected_people:
            person.kill() # person is dead

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
        people = self._people
        if severity > 5:
            people.make_babies() # triplets
        people.make_babies() # twins         

    def _get_affected_people(self, severity: int, percent: float) -> People:
        percent_affected = severity * percent
        people = self._people.get_people()
        random.shuffle(people)
        num_affected = int(len(people) * percent_affected)
        return random.sample(people, num_affected)
