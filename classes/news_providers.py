from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from typing import Dict

from pydantic import AnyUrl, ValidationError

from classes.logger import logger
from classes.models.news_provider import NewsProvider
from classes.models.providers_config import ProvidersConfig


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


@dataclass
class NewsProviders:
    news_providers: Dict[str, NewsProvider] = field(default_factory=dict)

    def register_provider(self, key: str, news_provider: NewsProvider):
        if key in self.news_providers:
            logger.warning(
                f"Provider {key} is already registered and will be overwritten."
            )
        self.news_providers[key] = news_provider

    def create_provider(self, key, config: NewsProvider):
        self.news_providers[key] = config

    @classmethod
    def init_from_config(cls, path: Path) -> "NewsProviders":
        providers_config = load_config(path)
        news_providers = cls()
        for provider, config in providers_config.providers.items():
            news_providers.register_provider(provider, config)
        return news_providers
