# Echoes of Eden

## Summary

Echoes of Eden is a civilization simulation. The simulation starts with a small, stable village in the middle of a
forest. Each person in the village has a set of tasks they can do, including gathering resources, building structures, 
having a family, and exploring. They are also aware of various personal metrics such as health, hunger, and family 
status. Villagers choose what tasks to do based on these personal metrics and various epsilon-greedy algorithms.

The simulation uses a 2D array to map the village and keep track of where each villager is. As villagers move around the
map, they can remember which structures they have passed. They use this memory to know where to find things later and 
determine what tasks need to be done. Villagers also have an inventory that enforces a limit on how many resources they 
can carry at a time.

After ____ iterations (mimicking ___ years), the simulation will finish and print various statistics on the village. 
These include graphs of ______, _____, and ______. The purpose of these is to use in analyzing how successful the 
simulation's decision-making algorithms are at keeping the village alive and thriving.

## How to Run

This program uses poetry to manage dependencies. Before running the program, install dependencies using 
`poetry shell` and `poetry install`. Then to run the simulation, run 'main.py'.

## Code Structure



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