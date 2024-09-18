import logging
import sys

# Configure the base logging, it applies to all loggers created
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],  # Ensure logs go to stdout
)


def get_logger(module_name):
    """
    Configure and provide a logger with the given module name.

    Parameters:
    - module_name (str): The name of the module requesting the logger.

    Returns:
    - logging.Logger: Configured logger instance with the specified module name.
    """
    logger = logging.getLogger(module_name)
    return logger
