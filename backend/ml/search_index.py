from pathlib import Path

import faiss
import pandas as pd
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image
from torchvision.models import resnet50, ResNet50_Weights

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
INDEX_PATH = ARTIFACTS_DIR / "faiss_index.index"
META_PATH = ARTIFACTS_DIR / "metadata.csv"

API_BASE = "http://127.0.0.1:8000"


def get_model_and_transform():
    weights = ResNet50_Weights.IMAGENET1K_V2
    model = resnet50(weights=weights)
    model.fc = torch.nn.Identity()
    model.eval()

    preprocess = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])
    return model, preprocess


def embed_image(image_path: str, device: str | None = None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model, preprocess = get_model_and_transform()
    model.to(device)

    img = Image.open(image_path).convert("RGB")
    x = preprocess(img).unsqueeze(0).to(device)

    with torch.no_grad():
        feat = model(x)
        feat = F.normalize(feat, dim=1)

    return feat.cpu().numpy().astype("float32")


def safe_value(row, key: str) -> str:
    value = row.get(key, "")
    if pd.isna(value):
        return ""
    return str(value)


def search_similar(image_path: str, k: int = 5):
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Index file not found: {INDEX_PATH}")

    if not META_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found: {META_PATH}")

    index = faiss.read_index(str(INDEX_PATH))
    df = pd.read_csv(META_PATH)

    query = embed_image(image_path)
    distances, indices = index.search(query, k)

    results = []
    for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), start=1):
        row = df.iloc[int(idx)]
        filename = Path(row["image_path"]).name

        results.append({
            "rank": rank,
            "id": int(idx),
            "image_path": safe_value(row, "image_path"),
            "image_url": f"{API_BASE}/images/{filename}",
            "distance": float(dist),
            "product_name": safe_value(row, "productDisplayName"),
            "gender": safe_value(row, "gender"),
            "master_category": safe_value(row, "masterCategory"),
            "sub_category": safe_value(row, "subCategory"),
            "article_type": safe_value(row, "articleType"),
            "base_colour": safe_value(row, "baseColour"),
            "season": safe_value(row, "season"),
            "usage": safe_value(row, "usage"),
        })

    return results