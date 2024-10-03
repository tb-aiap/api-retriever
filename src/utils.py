import logging
import logging.config

import yaml

logger = logging.getLogger(__name__)


def setup_logging(
    logging_config_path="./conf/logging.yaml", default_level=logging.INFO
):
    """Set up configuration for logging utilities."""
    try:
        with open(logging_config_path, "rt", encoding="utf-8") as file:
            log_config = yaml.safe_load(file.read())
        logging.config.dictConfig(log_config)

    except Exception as error:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=default_level,
        )
        logger.info(error)
        logger.info("Logging config file is not found. Basic config is being used.")


def hms(seconds: int) -> str:
    """Helper function to format epoch time into hh:mm:ss

    Args:
        seconds (int): Epoch time in seconds

    Returns:
        str: Formatted str, example 00h :45m :50s
    """
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60
    return "{:02d}h :{:02d}m :{:02d}s".format(h, m, s)
