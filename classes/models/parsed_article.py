from pydantic import BaseModel


class ParsedArticle(BaseModel):
    title: str
    url: str
    authors: list[str]
    body: str
