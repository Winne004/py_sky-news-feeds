from pathlib import Path


from classes.services.article_parsers import NewspaperArticleParser
from classes.services.feed_parsers import FeedParser
from classes.services.feed_service import FeedService
from classes.services.news_providers import NewsProviders
from classes.services.orchestrator import Orchestrator


if __name__ == "__main__":
    config_directory = Path(__file__).parent / "config" / "news_providers.json"
    news_providers = NewsProviders.init_from_config(path=config_directory)

    Orchestrator(
        article_parser=NewspaperArticleParser(),
        feed_service=FeedService,
        feed_parser=FeedParser,
        news_providers=news_providers,
    ).process(limit=5)

    # for news_provider in news_providers.providers:
    #     print(
    #         FeedService(
    #             parser=FeedParser, new_provider=news_provider
    #         ).parse_all_categories(limit=5)
    #     )
