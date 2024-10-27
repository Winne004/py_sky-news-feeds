from enum import Enum
import logging
from typing import List
import feedparser
from pydantic import BaseModel


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
    title: str
    link: str


class Entries(BaseModel):
    entries: List[Entry]


logger = logging.getLogger(__name__)


class FeedParser:
    def __init__(self, base_url):
        """
        Initialize the FeedParser with the base URL.
        """
        self.base_url = base_url

    def parse(self, path, limit=None):
        """
        Parse the RSS feed from the given path. Optionally limit the number of entries returned.
        """

        if limit and limit < 1:
            raise ValueError("Limit must be > 0")

        try:
            url = self.base_url + path
            logger.info("Fetching feed from %s", url)
            feed = feedparser.parse(url)
            entries = feed.get("entries", [])
            return Entries(entries=entries[:limit] if limit else entries)

        except Exception as e:
            logger.error("Error parsing feed {%s + %s}: %s", self.base_url, path, e)

    def parse_all_categories(self, path: NewsCategory, limit=None):

        return {category.name: self.parse(category.value, limit) for category in path}


class News(FeedParser):
    """
    Class to handle various news categories from Sky News feeds.
    """

    def __init__(self):
        super().__init__("https://feeds.skynews.com/feeds/rss")

    def get_feed(self, category: NewsCategory, limit=None):
        """
        Get a feed based on the category. Optionally limit the number of entries returned.
        """
        return self.parse(category.value, limit)

    def available_categories(self):
        """
        Return a list of available news categories.
        """
        return [category.name for category in NewsCategory]


c = News().parse_all_categories(NewsCategory)
print(c)
