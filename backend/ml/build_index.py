import os
from pathlib import Path

import faiss                   # type: ignore
import numpy as np
import pandas as pd
import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.models import resnet50, ResNet50_Weights
from tqdm.auto import tqdm

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "myntradataset"
IMAGES_DIR = DATASET_DIR / "images"
STYLES_CSV = DATASET_DIR / "styles.csv"

ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDINGS_NPY = ARTIFACTS_DIR / "embeddings.npy"
METADATA_CSV = ARTIFACTS_DIR / "metadata.csv"
FAISS_INDEX = ARTIFACTS_DIR / "faiss_index.index"


def load_metadata(max_items: int | None = None) -> pd.DataFrame:
    # Try a robust read first
    try:
        df = pd.read_csv(
            STYLES_CSV,
            engine="python",
            on_bad_lines="skip"  # pandas >= 1.3
        )
    except TypeError:
        # Older pandas: fall back to error_bad_lines=False, warn_bad_lines=False
        df = pd.read_csv(
            STYLES_CSV,
            engine="python",
            error_bad_lines=False,
            warn_bad_lines=False,
        )

    if "id" not in df.columns:
        raise ValueError("styles.csv must contain an 'id' column")

    df["image_path"] = df["id"].apply(
        lambda x: IMAGES_DIR / f"{int(x)}.jpg"
    )

    df = df[df["image_path"].apply(lambda p: p.exists())].reset_index(drop=True)

    if max_items is not None:
        df = df.head(max_items).reset_index(drop=True)

    print(f"Loaded {len(df)} clean rows from styles.csv")
    return df


def get_model_and_transform():
    weights = ResNet50_Weights.IMAGENET1K_V2
    model = resnet50(weights=weights)
    model.fc = torch.nn.Identity()
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)

    # Use standard ImageNet normalization constants
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    preprocess = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])
    return model, preprocess

def compute_embeddings(df: pd.DataFrame, batch_size: int = 32, device: str | None = None) -> np.ndarray:
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model, preprocess = get_model_and_transform()
    model.to(device)

    vectors: list[np.ndarray] = []
    total_batches = (len(df) + batch_size - 1) // batch_size

    with torch.no_grad():
        for start in tqdm(
            range(0, len(df), batch_size),
            total=total_batches,
            desc="Embedding images",
            unit="batch"
        ):
            batch = df.iloc[start:start + batch_size]
            images = []

            for path in batch["image_path"]:
                img = Image.open(path).convert("RGB")
                images.append(preprocess(img))

            batch_tensor = torch.stack(images).to(device)
            feats = model(batch_tensor)
            feats = torch.nn.functional.normalize(feats, dim=1)
            vectors.append(feats.cpu().numpy())

    embeddings = np.concatenate(vectors, axis=0)
    return embeddings.astype("float32")

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def main():
    print(f"Loading metadata from {STYLES_CSV} ...")
    df = load_metadata()  # start with 5k items
    print(f"Found {len(df)} images with metadata and files.")

    print("Computing embeddings with ResNet50...")
    embeddings = compute_embeddings(df, batch_size=16)  # smaller batch
    print(f"Embeddings shape: {embeddings.shape}")

    print(f"Saving embeddings to {EMBEDDINGS_NPY}")
    np.save(EMBEDDINGS_NPY, embeddings)

    print(f"Saving metadata to {METADATA_CSV}")
    df.to_csv(METADATA_CSV, index=False)

    print("Building FAISS index (cosine via inner product on normalized vectors)...")
    index = build_faiss_index(embeddings)

    print(f"Saving FAISS index to {FAISS_INDEX}")
    faiss.write_index(index, str(FAISS_INDEX))

    print("Done.")


if __name__ == "__main__":
    main()