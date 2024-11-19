# Echoes of Eden

## Summary

Echoes of Eden is a civilization simulation. The simulation starts with a small, stable village in the middle of a
forest. Each person in the village has a set of tasks they can do, including gathering resources, building structures, 
having a family, and exploring. They are also aware of various personal metrics such as health, hunger, and family 
status. Villagers choose what tasks to do based on these personal metrics, and by using various epsilon-greedy 
algorithms.

The simulation uses a 2D array to map the village and keep track of where each villager is. As villagers move around the
map, they can remember which structures they have passed. They use this memory to know where to find things later and 
determine what tasks need to be done. Villagers also have an inventory that enforces a limit on how many resources they 
can carry at a time.

After a set amount of iterations (mimicking some amount of years), the simulation will finish and print graphs and 
statistics about the village. The purpose of these is for use in analyzing how successful the simulation's 
decision-making algorithms are at keeping the village alive and thriving.

## How to Run

This program uses poetry to manage dependencies. Before running the program, install dependencies using 
`poetry shell` and `poetry install`. Then to run the simulation, run 'main.py'.

## Code Structure

The project directories are organized like so:


src
* `logger.py`: logs messages to the console about what is happening in the simulation as it runs
* `main.py`: runs the simulation
* `settings.py`: loads settings from the settings.yaml file into a global 'settings' variable
* simulation
  * `simulation.py`: the actual simulation: stores people, iterations, and grid, and contains methods for creating disasters and running the simulation
  * grid
    * `disjoint_set.py`: 
    * `grid.py`: a 2D array for mapping the simulation spatially, including locations of structures and people
    * `grid_disaster_generator.py`: generates grid-related disasters like mine disaster, stolen resources, or forest fire
    * `grid_generator.py`: generates a unique grid each time, with a small starting village and surrounding forest
    * `location.py`: handles logic about a specific location, such as travel time to another place, or determining what's nearby
    * `structure_generator.py`: generates structures within the grid
    * `temperature.py`: manages the temperature for every day of the year; temperature is taken from a normal distribution, using a mean from a sin wave that spans the year
    * structure
      * `structure.py`: structure class, handles location/placement of structure on grid
      * `structure_factory.py`: 
      * `structure_type.py`: 
      * store
        * `barn.py`: 
        * `home.py`: 
        * `store.py`: 
      * work
        * `farm.py`: 
        * `mine.py`: 
        * `tree.py`: 
        * `work.py`: 
        * construction
          * `construction.py`:
          * `construction_barn.py`: 
          * `construction_farm.py`: 
          * `construction_home.py`: 
          * `construction_mine.py`: 
  * people
    * `home_manager.py`: 
    * `people.py`: 
    * `people_disaster_generator.py`: 
    * `people_generator.py`: 
    * person
      * `backpack.py`: handles all logic for a person's inventory
      * `memories.py`: handles all logic for a person's memory
      * `person.py`: handles all logic for a single person, including traits and actions
      * movement
        * `move_result.py`: defines class MoveResult for storing if a call to move_to succeeded and resulted in a structure 
        * `mover.py`: handles all lower-level logic for moving a person around the grid
        * `navigator.py`: handles all higher-level logic for moving a person around the grid
        * `vision.py`: handles all logic for what a person can see around them as they move around the grid
      * scheduler
        * `scheduler.py`: 
        * task
          * `eat.py`:
          * `explore.py`: 
          * `find_home.py`: 
          * `find_spouse`: 
          * `task.py`: 
          * `task_factory.py`: 
          * `task_type.py`: 
          * `transport.py`: 
          * construction
            * `build.py`: 
            * `build_barn.py`: 
            * `build_farm.py`: 
            * `build_home.py`: 
            * `build_mine.py`: 
          * start_construction
            * `start_barn_construction.py`: 
            * `start_construction.py`: 
            * `start_farm_construction.py`: 
            * `start_home_construction.py`: 
            * `start_mine_construction.py`: 
          * work
            * `chop_tree.py`: 
            * `work.py`: 
            * `work_farm.py`: 
            * `work_mine.py`: 
  * visualization
    * `visualizer.py`:
    * plotter
      * `grid_plotter.py`: 
      * `state_plotter.py`:
    * state
      * `grid_disaster_state.py`: 
      * `grid_state.py`: 
      * `people_disaster_state.py`: 
      * `people_state.py`: 
      * `resource_state.py`: 
      * `state.py`: 
      * `task_state.py`: 


## Dev Tools

1. A more comprehensive tool that checks for errors, enforces a coding standard, and looks for code smells.
   - `poetry run pylint src/**/*.py`
2. A static type checker for Python that can help catch type errors.
   - `poetry run mypy src/**/*.py`
3. An opinionated code formatter that enforces a consistent style.
   - `poetry run black src/**/*.py`
   - `poetry run isort src/**/*.py`
   - `poetry run autoflake --in-place --remove-unused-variables src/**/*.py`

## Licence

This project uses the MIT license. (See the 'LICENSE' file in this directory.)