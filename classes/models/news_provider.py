from enum import Enum
from typing import Type

from pydantic import AnyUrl, BaseModel, field_validator


class NewsProvider(BaseModel):
    categories: Type[Enum]
    base_url: AnyUrl

    @field_validator("categories", mode="before")
    @classmethod
    def validate_categories(cls, categories):
        return Enum("BaseNewsCategory", categories, type=str)
