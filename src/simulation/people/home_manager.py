from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple, Optional

from src.simulation.grid.location import Location

if TYPE_CHECKING:
    from src.simulation.people.people import People
    from src.simulation.people.person.person import Person


class HomeManager:
    def __init__(self, people: People):
        self._people = people

    def swap_homes(self) -> None:
        # Step 1: Get the people who are far from their work centers
        far_people: Dict[Person, Location] = self._get_far_walking_people()

        # Step 2: Remove people whose homes are near their work centers
        far_people = self._filter_people_near_centers(far_people)

        # Step 3: Match and swap homes for people within 20 blocks
        matches: List[Tuple[Person, Person]] = self._find_matches(far_people, 20)
        self._swap_home_assignments(matches)

        # Step 4: Remove matched people from the list
        self._remove_matched_people(far_people, matches)

        # Step 5: Match and swap homes for people within 40 units
        matches = self._find_matches(far_people, 40)
        self._swap_home_assignments(matches)

    @staticmethod
    def _remove_matched_people(
        far_people: Dict[Person, Location], matches: List[Tuple[Person, Person]]
    ) -> None:
        """Remove matched people from the far_people list"""
        for person1, person2 in matches:
            far_people.pop(person1, None)
            far_people.pop(person2, None)

    @staticmethod
    def _swap_home_assignments(matches: List[Tuple[Person, Person]]) -> None:
        """Swap homes between matched people"""
        for person1, person2 in matches:
            home1, home2 = person1.get_home(), person2.get_home()
            person1.assign_home(home2)
            person2.assign_home(home1)

    @staticmethod
    def _find_matches(
        far_people: Dict[Person, Location], distance: int
    ) -> List[Tuple[Person, Person]]:
        """Find pairs of people whose homes are within the given distance"""
        matches = []
        matched_people = set()

        for person1, center1 in far_people.items():
            if person1 in matched_people:
                continue

            for person2, center2 in far_people.items():
                if person2 in matched_people or person1 == person2:
                    continue

                if person1.get_home().get_location().is_near(center2, distance):
                    matches.append((person1, person2))
                    matched_people.update([person1, person2])

        return matches

    @staticmethod
    def _filter_people_near_centers(
        far_people: Dict[Person, Location]
    ) -> Dict[Person, Location]:
        """Remove people whose homes are already near their work centers"""
        to_remove = [
            person
            for person, center in far_people.items()
            if person.get_home().get_location().is_near(center, 30)
        ]

        # Remove the filtered people from the far_people dictionary
        for person in to_remove:
            far_people.pop(person, None)

        return far_people

    def _get_far_walking_people(self) -> Dict[Person, Location]:
        """Return a dictionary of people and the center of their work locations"""
        far_people: Dict[Person, Location] = {}

        for person in self._people:
            if not person.get_spouse():
                center = self._calculate_center(person.get_work_structures())
                if center:
                    far_people[person] = center

        for person in self._people.get_married_people():
            person_center = self._calculate_center(person.get_work_structures())
            spouse_center = self._calculate_center(
                person.get_spouse().get_work_structures()
            )
            combined_center = self._calculate_center([person_center, spouse_center])

            if combined_center:
                far_people[person] = combined_center

        return far_people

    @staticmethod
    def _calculate_center(structures: List[Location]) -> Optional[Location]:
        """Calculate the average location of a list of structures"""
        if not structures:
            return None

        total_x, total_y = sum(loc.x for loc in structures), sum(
            loc.y for loc in structures
        )
        avg_x, avg_y = total_x // len(structures), total_y // len(structures)

        return Location(avg_x, avg_y)
