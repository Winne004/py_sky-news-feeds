from enum import Enum
from typing import List, Optional, Type

from pydantic import AnyUrl
from classes.utils.logger import logger
from classes.services.feed_parsers import FeedParserInterface
from classes.models.entries import Entries, EntriesByCategory
from classes.models.news_provider import NewsProvider


class FeedService:

    def __init__(self, parser: FeedParserInterface):
        self.parser: FeedParserInterface = parser

    def parse_feed(
        self,
        base_url: str,
        path: str,
        limit: Optional[int] = None,
    ) -> Entries:
        """
        Parse the RSS feed from the given path and return entries. Optionally limit the number of entries returned.
        """
        if limit is not None and limit < 1:
            raise ValueError("Limit must be greater than 0")

        url = self.build_url(base_url=base_url, path=path)
        logger.info("Fetching feed from %s", url)
        return self.parser.parse(url=url, limit=limit)

    def build_url(self, base_url: AnyUrl, path: str) -> str:
        return f"{base_url}{path}"

    def parse_all_categories(
        self, news_provider: NewsProvider, limit: Optional[int] = None
    ) -> List[Entries]:
        """
        Parse feeds from all categories and return a dictionary of entries by category name.
        """

        return EntriesByCategory(
            category={
                category.name: self.parse_feed(
                    base_url=news_provider.base_url, path=category.value, limit=limit
                )
                for category in news_provider.categories
            }
        )
