from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


from classes.utils.load_config import load_config
from classes.utils.logger import logger
from classes.models.news_provider import NewsProvider


@dataclass
class NewsProviders:
    news_providers: Dict[str, NewsProvider] = field(default_factory=dict)

    def register_provider(self, key: str, news_provider: NewsProvider):
        if key in self.news_providers:
            logger.warning(
                "Provider %s is already registered and will be overwritten.", key
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

    @property
    def providers(self) -> List[NewsProvider]:
        """
        A property that returns a list of all registered NewsProvider instances.
        """
        return list(self.news_providers.values())
