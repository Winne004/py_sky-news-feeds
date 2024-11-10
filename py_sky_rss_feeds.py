from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import List, Optional, Type
from urllib.error import HTTPError

import feedparser

from classes.logger import logger
from classes.models.entries import Entries
from classes.models.news_provider import NewsProvider
from classes.news_providers import NewsProviders


class FeedParserInterface(ABC):
    @abstractmethod
    def parse(self, url: str, limit: int = None) -> Entries:
        """Parses a feed from the given URL and returns the result."""
        pass


class FeedParser(FeedParserInterface):
    def parse(self, url: str, limit: int = None) -> Entries:
        if limit and limit < 1:
            raise ValueError("Limit must be greater than 0")

        try:
            feed = feedparser.parse(url)

            if feed:
                entries_data = feed.get("entries", [])
                entries = (
                    [entry for entry in entries_data[:limit]] if limit else entries_data
                )
                return Entries(entries=entries)
            return Entries(entries=[])

        except HTTPError as e:
            logger.error("HTTP error %s fetching feed %s: %s", e.code, url, e)
            if e.code == 404:
                logger.error("Nonexistent RSS feed at %s", url)
            raise

        except Exception as e:
            logger.error("Unexpected error parsing feed from %s: %s", url, e)
            raise


class FeedService:

    def __init__(self, parser: Type[FeedParserInterface], new_provider: NewsProvider):
        self.parser: FeedParserInterface = parser()
        self.base_url = str(new_provider.base_url)
        self.categories = new_provider.categories

    def parse_feed(self, path: str, limit: Optional[int] = None) -> Entries:
        """
        Parse the RSS feed from the given path and return entries. Optionally limit the number of entries returned.
        """
        if limit is not None and limit < 1:
            raise ValueError("Limit must be greater than 0")

        url = self.build_url(path=path)
        logger.info("Fetching feed from %s", url)
        return self.parser.parse(url=url, limit=limit)

    def build_url(self, path: str):
        return self.base_url + path

    def parse_all_categories(self, limit: Optional[int] = None) -> dict:
        """
        Parse feeds from all categories and return a dictionary of entries by category name.
        """
        return {
            category.name: self.parse_feed(category.value, limit)
            for category in self.categories
        }

    def parse_category(self, category: Enum, limit: Optional[int] = None) -> Entries:
        """
        Parse feeds from all categories and return a dictionary of entries by category name.
        """
        return self.parse_feed(category.value, limit)

    def available_categories(self) -> List[str]:
        """
        Return a list of available news categories.
        """
        return [category.name for category in self.categories]


if __name__ == "__main__":
    config_directory = Path(__file__).parent / "config" / "news_providers.json"
    news_providers = NewsProviders.init_from_config(path=config_directory)
    for news_provider in news_providers.news_providers.values():
        print(
            FeedService(
                parser=FeedParser, new_provider=news_provider
            ).parse_all_categories(limit=5)
        )
