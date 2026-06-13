from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ml.search_index import search_similar

app = FastAPI(title="StyleLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
IMAGES_DIR = BASE_DIR / "ml" / "dataset" / "myntradataset" / "images"

UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")


@app.get("/")
def root():
    return {"message": "StyleLens API is running"}


@app.post("/search")
async def search(file: UploadFile = File(...), k: int = 5):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file")

    temp_path = UPLOAD_DIR / file.filename

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = search_similar(str(temp_path), k=k)
    return {"results": results}