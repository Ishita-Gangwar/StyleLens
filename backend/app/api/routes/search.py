from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from app.schemas.product import ProductResult
from app.schemas.search import ImageSearchResponse

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/image", response_model=ImageSearchResponse)
async def search_by_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    try:
        image = Image.open(BytesIO(content))
        width, height = image.size
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    results = [
        ProductResult(
            source="amazon",
            title="Demo Product 1",
            product_url="https://example.com/product-1",
            image_url="https://via.placeholder.com/300",
            price="999",
            rating="4.2",
        ),
        ProductResult(
            source="local",
            title="Demo Product 2",
            product_url="https://example.com/product-2",
            image_url="https://via.placeholder.com/300",
            price="1299",
            rating="4.5",
        ),
    ]

    return ImageSearchResponse(
        filename=file.filename or "unknown",
        content_type=file.content_type,
        size_bytes=len(content),
        width=width,
        height=height,
        results=results,
    )