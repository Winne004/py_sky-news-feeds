from pathlib import Path


from classes.services.article_parsers import NewspaperArticleParser
from classes.services.feed_parsers import FeedParser
from classes.services.feed_service import FeedService
from classes.services.news_providers import NewsProviders
from classes.services.orchestrator import Orchestrator


if __name__ == "__main__":
    config_directory = Path(__file__).parent / "config" / "news_providers.json"
    news_providers = NewsProviders.init_from_config(path=config_directory)

    orchestrator = Orchestrator(
        article_parser=NewspaperArticleParser(),
        feed_service=FeedService,
        feed_parser=FeedParser,
        news_providers=news_providers,
    )
    orchestrator.process(limit=5)

    pass
