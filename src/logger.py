import os
import sys

from loguru import logger


def setup_logger(mode: str = "dev") -> None:
    # Create a logs directory if it doesn't exist
    log_dir: str = "../logs"
    os.makedirs(log_dir, exist_ok=True)

    # Define log file path
    log_file_path: str = os.path.join(log_dir, "app.log")

    # Remove the default logger
    logger.remove()

    # Set log level based on mode
    console_log_level: str = "DEBUG" if mode == "dev" else "INFO"
    file_log_level: str = "DEBUG"  # Always log DEBUG to file

    # Configure the logger
    logger.add(
        sys.stdout,
        level=console_log_level,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    )  # Log to console
    logger.add(
        log_file_path,
        rotation="1 MB",  # Rotate after 1 MB
        retention="10 days",  # Keep logs for 10 days
        compression="zip",  # Compress old logs
        level=file_log_level,  # Log level for the file
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    )  # Log format

    logger.add(
        os.path.join(log_dir, "error.log"),
        level="ERROR",
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    )


if __name__ == "__main__":
    # Example usage: Pass 'prod' or 'dev' to setup the logger
    setup_logger(mode="dev")  # Change to 'prod' for production mode

    logger.info("Logger is set up and ready to use!")
    logger.debug("This is a debug message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
