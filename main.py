from pathlib import Path


from classes.services.feed_parsers import FeedParser
from classes.services.feed_service import FeedService
from classes.services.news_providers import NewsProviders


if __name__ == "__main__":
    config_directory = Path(__file__).parent / "config" / "news_providers.json"
    news_providers = NewsProviders.init_from_config(path=config_directory)
    for news_provider in news_providers.providers:
        print(
            FeedService(
                parser=FeedParser, new_provider=news_provider
            ).parse_all_categories(limit=5)
        )
