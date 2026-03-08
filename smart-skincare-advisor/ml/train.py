"""
Training script for the Skin Care CNN.

Usage:
    python train.py --dataset ../dataset --epochs 30 --batch_size 32 --lr 1e-3
"""

import argparse
import os
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR

# Local imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
from model import get_model, SkinCareCNN
from dataset_loader import get_dataloaders


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Train SkinCare CNN")
    p.add_argument("--dataset",    type=str,   default="../dataset",  help="Path to dataset root")
    p.add_argument("--epochs",     type=int,   default=30)
    p.add_argument("--batch_size", type=int,   default=32)
    p.add_argument("--lr",         type=float, default=1e-3)
    p.add_argument("--val_split",  type=float, default=0.2)
    p.add_argument("--output",     type=str,   default="skin_cnn.pth",help="Output model path")
    p.add_argument("--workers",    type=int,   default=2)
    return p.parse_args()


# ── Training helpers ──────────────────────────────────────────────────────────

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct  += preds.eq(labels).sum().item()
        total    += images.size(0)

    return total_loss / total, correct / total


def validate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)
            _, preds = outputs.max(1)
            correct  += preds.eq(labels).sum().item()
            total    += images.size(0)

    return total_loss / total, correct / total


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args   = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[train] Device : {device}")

    # Data
    train_loader, val_loader, class_names = get_dataloaders(
        args.dataset,
        batch_size=args.batch_size,
        val_split=args.val_split,
        num_workers=args.workers,
    )

    # Model
    model = get_model(num_classes=len(class_names)).to(device)
    print(f"[train] Classes: {class_names}")

    # Loss / Optimizer / Scheduler
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = StepLR(optimizer, step_size=10, gamma=0.5)

    best_val_acc = 0.0
    output_path  = Path(args.output)

    print(f"\n{'Epoch':>6}  {'Train Loss':>11}  {'Train Acc':>10}  {'Val Loss':>9}  {'Val Acc':>8}")
    print("-" * 60)

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()

        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        va_loss, va_acc = validate(model, val_loader, criterion, device)
        scheduler.step()

        elapsed = time.time() - t0
        print(f"{epoch:>6}  {tr_loss:>11.4f}  {tr_acc:>9.2%}  {va_loss:>9.4f}  {va_acc:>7.2%}  [{elapsed:.1f}s]")

        # Save best checkpoint
        if va_acc > best_val_acc:
            best_val_acc = va_acc
            torch.save(model.state_dict(), str(output_path))
            print(f"         ↳ Saved best model → {output_path}  (val_acc={va_acc:.2%})")

    print(f"\n[train] Done. Best val accuracy: {best_val_acc:.2%}")
    print(f"[train] Model saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
