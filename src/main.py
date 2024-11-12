from src.settings import settings, environment # this must be imported first
from src.logger import logger, setup_logger
from src.simulation.simulation import Simulation
from src.simulation.visualization.visualizer import Visualizer

def main() -> None:
    setup_logger(environment)
    logger.info("Starting the simulation program.")
    
    # Access settings via the globally initialized object
    max_simulations = settings.get("max_simulations", 10)

    for i in range(max_simulations):
        logger.info(f"Running simulation {i + 1}")
        simulation: Simulation = Simulation()
        visualizer: Visualizer = simulation.run()
        visualizer.display_town_slide_show()
        visualizer.display_simulation_stats()

        logger.info(f"Simulation {i + 1} completed")


if __name__ == "__main__":
    main()
