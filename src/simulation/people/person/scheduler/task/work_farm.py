from people.person.person import Person
from people.person.scheduler.task.task import Task
from simulation import Simulation

class WorkFarm(Task):
    def __init__(self, simulation: Simulation, person: Person) -> None:
        super().__init__(simulation, person, 5) # TODO: change priority
    
    def execute(self) -> None:
        if not self._person.at_farm():
            self._person.find_farm_to_work_at()
        else:
            self._person.work_farm()
            self._finished()
            # TODO: do we need to specify here that work_farm might take multiple turns?
                # --> should that be implemented with a tally or something?