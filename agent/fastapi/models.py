from pydantic import BaseModel
from typing import List

class DocumentResponse(BaseModel):
    available_documents: List[str]

class ArxivResult(BaseModel):
    title: str
    summary: str
    published: str
    authors: List[str]
    link: str

class WebSearchResult(BaseModel):
    title: str
    snippet: str
    link: str
