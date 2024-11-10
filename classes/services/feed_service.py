from enum import Enum
from typing import List, Optional, Type
from classes.utils.logger import logger
from classes.services.feed_parsers import FeedParserInterface
from classes.models.entries import Entries, EntriesByCategory
from classes.models.news_provider import NewsProvider


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

    def parse_all_categories(self, limit: Optional[int] = None) -> List[Entries]:
        """
        Parse feeds from all categories and return a dictionary of entries by category name.
        """
        return EntriesByCategory(
            category={
                category.name: self.parse_feed(category.value, limit)
                for category in self.categories
            }
        )

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
