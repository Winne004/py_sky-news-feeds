from typing import Dict

from pydantic import BaseModel
from classes.models.news_provider import NewsProvider


class ProvidersConfig(BaseModel):
    providers: Dict[str, NewsProvider]
