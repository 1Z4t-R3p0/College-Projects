"""
Dataset loader for skin condition images.
Expects the dataset directory to follow the structure:
  dataset/
    acne/       *.jpg / *.png
    eczema/     ...
    melanoma/   ...
    ...
"""

import os
from pathlib import Path
from typing import Tuple

import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

# ── Default image transforms ──────────────────────────────────────────────────

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

TRAIN_TRANSFORMS = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.2),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

VAL_TRANSFORMS = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

PREDICT_TRANSFORMS = VAL_TRANSFORMS  # alias used by predict.py


def get_dataloaders(
    dataset_dir: str,
    batch_size: int = 32,
    val_split: float = 0.2,
    num_workers: int = 2,
    seed: int = 42,
) -> Tuple[DataLoader, DataLoader, list]:
    """
    Build train / validation DataLoaders from a folder-labelled dataset.

    Returns
    -------
    train_loader, val_loader, class_names
    """
    dataset_dir = Path(dataset_dir)
    if not dataset_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    # Load the full dataset with training transforms first (we'll swap val set later)
    full_dataset = datasets.ImageFolder(root=str(dataset_dir), transform=TRAIN_TRANSFORMS)
    class_names  = full_dataset.classes
    total      = len(full_dataset)

    # For very small datasets (e.g. demo with 7 images), use all for training
    if total < 10:
        print(f"[dataset] Tiny dataset detected ({total} images). Using all for training.")
        train_ds = full_dataset
        val_ds   = full_dataset # Use same for validation just for the metrics
        train_size = total
        val_size = total
    else:
        val_size   = int(total * val_split)
        train_size = total - val_size
        generator = torch.Generator().manual_seed(seed)
        train_ds, val_ds = random_split(full_dataset, [train_size, val_size], generator=generator)
        # Override val transform
        val_ds.dataset = datasets.ImageFolder(root=str(dataset_dir), transform=VAL_TRANSFORMS)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    print(f"[dataset] Classes  : {class_names}")
    print(f"[dataset] Train    : {train_size} images")
    print(f"[dataset] Val      : {val_size} images")

    return train_loader, val_loader, class_names


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    tl, vl, classes = get_dataloaders(root, batch_size=4)
    batch = next(iter(tl))
    print(f"Batch shape: {batch[0].shape}, Labels: {batch[1]}")
