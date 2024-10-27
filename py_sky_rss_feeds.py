from enum import Enum
import logging
from typing import List, Optional
from urllib.error import HTTPError
import feedparser
from pydantic import BaseModel, Field

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


class FeedParser:
    def __init__(self, base_url: str):
        """
        Initialize the FeedParser with the base URL for the RSS feeds.
        """
        self.base_url = base_url

    def parse(self, path: str, limit: Optional[int] = None) -> Entries:
        """
        Parse the RSS feed from the given path and return entries. Optionally limit the number of entries returned.
        """
        if limit and limit < 1:
            raise ValueError("Limit must be greater than 0")

        url = self.base_url + path
        logger.info("Fetching feed from %s", url)

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

    def parse_all_categories(self, limit: Optional[int] = None) -> dict:
        """
        Parse feeds from all categories and return a dictionary of entries by category name.
        """
        return {
            category.name: self.parse(category.value, limit)
            for category in NewsCategory
        }


class News(FeedParser):
    """
    Class to handle various news categories from Sky News feeds.
    """

    def __init__(self):
        super().__init__("https://feeds.skynews.com/feeds/rss")

    def get_feed(self, category: NewsCategory, limit: Optional[int] = None) -> Entries:
        """
        Get a feed based on the category and return entries. Optionally limit the number of entries returned.
        """
        return self.parse(category.value, limit)

    def available_categories(self) -> List[str]:
        """
        Return a list of available news categories.
        """
        return [category.name for category in NewsCategory]


if __name__ == "__main__":
    news = News()
    feeds = news.parse_all_categories(limit=5)
