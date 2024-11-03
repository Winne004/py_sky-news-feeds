from abc import ABC, abstractmethod
from enum import Enum
import logging
from typing import List, Optional
from urllib.error import HTTPError
import feedparser
from pydantic import AnyUrl, BaseModel, Field

# Configure logger for the module
logger = logging.getLogger(__name__)


class NewsCategory(str, Enum):
    HOME = "/home.xml"
    UK = "/uk.xml"
    WORLD = "/world.xml"
    US = "/us.xml"
    BUSINESS = "/business.xml"
    POLITICS = "/politics.xml"
    TECHNOLOGY = "/technology.xml"
    ENTERTAINMENT = "/entertainment.xml"
    STRANGE = "/strange.xml"


class Entry(BaseModel):
    title: str = Field(..., description="Title of the news entry")
    link: str = Field(..., description="Link to the full news article")


class Entries(BaseModel):
    entries: List[Entry | None]


class FeedParserInterface(ABC):
    @abstractmethod
    def parse(self, url: str, limit: int = None) -> Entries:
        """Parses a feed from the given URL and returns the result."""
        pass


class FeedParser(FeedParserInterface):
    def parse(self, url: str, limit: int = None) -> Entries:
        try:
            feed = feedparser.parse(url)

            if feed:
                entries_data = feed.get("entries", [])
                entries = (
                    [Entry(**entry) for entry in entries_data[:limit]]
                    if limit
                    else entries_data
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
    def __init__(
        self, base_url: str, parser: FeedParserInterface, categories: NewsCategory
    ):
        self.parser: FeedParserInterface = parser()
        self.base_url: str = str(AnyUrl(url=base_url))
        self.categories: NewsCategory = categories

    def parse_feed(self, path: str, limit: Optional[int] = None) -> Entries:
        """
        Parse the RSS feed from the given path and return entries. Optionally limit the number of entries returned.
        """
        if limit and limit < 1:
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

    def parse_category(
        self, category: NewsCategory, limit: Optional[int] = None
    ) -> Entries:
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
    news = FeedService(
        base_url="https://feeds.skynews.com/feeds/rss",
        parser=FeedParser,
        categories=NewsCategory,
    )
    feeds = news.parse_category(category=NewsCategory.HOME, limit=5)
    print(feeds)
