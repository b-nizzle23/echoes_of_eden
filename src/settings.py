import argparse
from dynaconf import Dynaconf

class Settings:
    def __init__(self, environment: str):
        """Initialize Settings and load environment-specific configurations."""
        self._environment = environment
        self._settings = self._load_settings()

    def _load_settings(self) -> Dynaconf:
        """Load settings from the environment-specific file and .env."""
        settings_file = f"../settings/{self._environment}_settings.yaml"
        return Dynaconf(
            settings_files=[settings_file],  # Use both settings file and .env
            environments=True,  # Enable environment-specific configuration
            load_dotenv=True  # Optionally load .env variables if needed
        )

    def get(self, key: str, default=None):
        """Get a configuration value by key."""
        return self._settings.get(key, default)

# Helper function to get environment from command line args
def get_environment() -> str:
    """Get the environment from command-line arguments (e.g., dev, prod)."""
    parser = argparse.ArgumentParser(description="Run the simulation program.")
    parser.add_argument(
        "--settings", type=str, default="dev", help="Specify the environment (default: dev)"
    )
    args = parser.parse_args()
    return args.settings

environment = get_environment()
settings = Settings(environment)  # This will initialize the global `settings` object
