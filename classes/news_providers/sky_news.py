from classes.models.baseNewsCategory import BaseNewsCategory
from classes.models.news_provider import NewsProvider


class SkyNewsCategories(BaseNewsCategory):
    HOME = "/home.xml"
    UK = "/uk.xml"
    WORLD = "/world.xml"
    US = "/us.xml"
    BUSINESS = "/business.xml"
    POLITICS = "/politics.xml"
    TECHNOLOGY = "/technology.xml"
    ENTERTAINMENT = "/entertainment.xml"
    STRANGE = "/strange.xml"


sky_news = NewsProvider(
    categories=SkyNewsCategories, base_url="https://feeds.skynews.com/feeds/rss"
)

print(sky_news.base_url)
