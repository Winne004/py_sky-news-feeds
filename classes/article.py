from abc import ABC, abstractmethod
from typing import Any
from newspaper import Article
from goose3 import Goose
from pydantic import AnyUrl, BaseModel, ValidationError
from classes.logger import logger


class ParsedArticle(BaseModel):
    title: str
    url: str
    authors: list[str]


class NewsArticleParserInterface(ABC):
    @abstractmethod
    def article_parse(self, article_url: str) -> Any:
        """Parses an article from the given URL and returns the result."""
        pass


class NewspaperArticleParser(NewsArticleParserInterface):
    def article_parse(self, article_url: str) -> Any:
        AnyUrl(url=article_url)
        newspaper_article = Article(url=article_url)
        newspaper_article.download()
        newspaper_article.parse()
        newspaper_article = ParsedArticle(
            title=newspaper_article.title,
            url=newspaper_article.url,
            authors=newspaper_article.authors,
        )
        return newspaper_article


class GooseArticleParser(NewsArticleParserInterface):
    def __init__(self):
        self.goose_extraction_object = Goose()

    def article_parse(self, article_url: str) -> Any:
        try:
            AnyUrl(url=article_url)
        except ValidationError as e:
            logger.error(f"Invalid URL provided: {e}")
            raise ValueError("Invalid article URL.") from e
        goose_article = self.goose_extraction_object.extract(article_url)
        goose_article = ParsedArticle(
            title=goose_article.title,
            url=goose_article.final_url,
            authors=goose_article.authors,
        )
        return goose_article


if __name__ == "__main__":
    article_parser = NewspaperArticleParser()
    article = article_parser.article_parse(
        "https://news.sky.com/story/kemi-badenoch-says-partygate-scandal-was-overblown-13247460"
    )

    print(article)

    article_parser = GooseArticleParser()
    article = article_parser.article_parse(
        "https://www.bbc.co.uk/news/articles/c5ypgjg2jrpo"
    )

    print(article)
