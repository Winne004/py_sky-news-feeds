from typing import List
from pydantic import BaseModel, Field


class Entry(BaseModel):
    title: str = Field(..., description="Title of the news entry")
    link: str = Field(..., description="Link to the full news article")


class Entries(BaseModel):
    entries: List[Entry | None]
