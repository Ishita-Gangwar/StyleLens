from pydantic import BaseModel
from typing import List
from app.schemas.product import ProductResult


class ImageSearchResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    width: int
    height: int
    results: List[ProductResult]