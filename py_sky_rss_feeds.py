from pathlib import Path


from classes.feed_parser import FeedParser
from classes.feed_service import FeedService
from classes.news_providers import NewsProviders


if __name__ == "__main__":
    config_directory = Path(__file__).parent / "config" / "news_providers.json"
    news_providers = NewsProviders.init_from_config(path=config_directory)
    for news_provider in news_providers.providers:
        print(
            FeedService(
                parser=FeedParser, new_provider=news_provider
            ).parse_all_categories(limit=5)
        )
