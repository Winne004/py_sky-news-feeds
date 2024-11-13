from typing import Dict, List
from pydantic import BaseModel, Field
from pydantic_core import Url


class Entry(BaseModel):
    title: str = Field(..., description="Title of the news entry")
    link: str = Field(..., description="Link to the full news article")


class Entries(BaseModel):
    entries: List[Entry | None]


class EntriesByCategory(BaseModel):
    category: Dict[str, Entries]


class CategoryByBaseUrl(BaseModel):
    provider: Dict[Url, EntriesByCategory]
