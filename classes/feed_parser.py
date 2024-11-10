from abc import ABC, abstractmethod
import feedparser
from urllib.error import HTTPError
from classes.logger import logger
from classes.models.entries import Entries


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
                entries = entries_data[:limit] if limit else entries_data
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
