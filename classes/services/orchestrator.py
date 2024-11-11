from abc import ABC, abstractmethod
from typing import List, Type

from classes.models.entries import CategoryByBaseUrl
from classes.models.parsed_article import ParsedArticle
from classes.services.article_parsers import NewspaperArticleParser

from classes.services.feed_parsers import FeedParser
from classes.services.feed_service import FeedService
from classes.services.news_providers import NewsProviders
from classes.utils.logger import logger


class OrchestratorInterface(ABC):
    @abstractmethod
    def process(self, data):
        pass


class Orchestrator:

    def __init__(
        self,
        article_parser: NewspaperArticleParser,
        feed_service: Type[FeedService],
        feed_parser: Type[FeedParser],
        news_providers: NewsProviders,
    ):
        self.article_parser = article_parser
        self.feed_parser = feed_parser
        self.news_providers = news_providers
        self.feed_service = feed_service
        self.providers_by_categories: CategoryByBaseUrl | None = None
        self.parsed_articles: List[ParsedArticle] | None = None

    def _fetch_categories_by_provider(self) -> CategoryByBaseUrl:
        categories_by_provider = {}
        for news_provider in self.news_providers.providers:

            feed_service = self.feed_service(self.feed_parser, news_provider)
            categories_by_provider[news_provider.base_url] = (
                feed_service.parse_all_categories()
            )

        return CategoryByBaseUrl(provider=categories_by_provider)

    def _parse_articles(self, limit):
        parsed_articles = []

        for provider in self.providers_by_categories.provider.values():
            for category in provider.category.values():
                entries = category.entries
                for entry in entries[:limit] if limit else entries:
                    try:
                        parsed_article = self.article_parser.article_parse(entry.link)
                        parsed_articles.append(parsed_article)
                    except Exception as e:
                        logger.error("Error parsing article %s: %s", entry.link, e)
        return parsed_articles

    def process(self, limit: int = None) -> List[ParsedArticle]:
        """
        Process all categories for each news provider and parse articles.

        Args:
            limit (Optional[int]): Maximum number of articles to process per category.

        Returns:
            List[ParsedArticle]: A list of parsed articles.
        """
        self.providers_by_categories = self._fetch_categories_by_provider()
        parsed_articles = self._parse_articles(limit)
        self.parsed_articles = parsed_articles
