from typing import Type, TypeVar

from pydantic import AnyUrl, BaseModel

from classes.models.baseNewsCategory import BaseNewsCategory


CategoryType = TypeVar("CategoryType", bound=BaseNewsCategory)


class NewsProvider(BaseModel):
    categories: Type[CategoryType]
    base_url: AnyUrl
