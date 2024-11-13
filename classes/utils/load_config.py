import json
from pathlib import Path


from pydantic import ValidationError

from classes.models.providers_config import ProvidersConfig
from classes.utils.logger import logger


def load_config(config_file_path: Path):
    try:
        with open(config_file_path, encoding="utf-8") as f:
            return ProvidersConfig(**json.load(f))

    except ValidationError as e:
        logger.error("Validation Error: %s", e)
        raise e

    except FileNotFoundError as e:
        logger.error("File Path Error: %s", e)
        raise e
