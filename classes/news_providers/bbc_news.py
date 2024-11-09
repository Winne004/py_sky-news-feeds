from classes.models.baseNewsCategory import BaseNewsCategory
from classes.models.news_provider import NewsProvider


class BBCNewsCategories(BaseNewsCategory):
    TOP_STORIES = "/rss.xml"
    UK = "/uk/rss.xml"
    WORLD = "/world/rss.xml"
    US = "/us.xml"
    BUSINESS = "/business/rss.xml"
    POLITICS = "/politics/rss.xml"
    TECHNOLOGY = "/technology/rss.xml"
    ENTERTAINMENT = "/entertainment_and_arts/rss.xml"


bbc_news = NewsProvider(
    categories=BBCNewsCategories, base_url="https://feeds.bbci.co.uk/news"
)
