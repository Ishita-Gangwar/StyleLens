from pydantic import BaseModel
from typing import Optional


class ProductResult(BaseModel):
    source: str
    title: str
    product_url: str
    image_url: Optional[str] = None
    price: Optional[str] = None
    rating: Optional[str] = None