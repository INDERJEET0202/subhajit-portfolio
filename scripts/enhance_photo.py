#!/usr/bin/env python3
"""One-off: enhance the faded profile photo and drop it into assets/img/.

Usage:
    python3 scripts/enhance_photo.py <input_image> [output_name]
"""
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "img"


def enhance(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")

    # Lift the washed-out look: stretch the histogram so blacks/whites
    # actually reach 0/255 instead of sitting in a hazy mid-range.
    im = ImageOps.autocontrast(im, cutoff=1)

    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = ImageEnhance.Brightness(im).enhance(1.03)
    im = ImageEnhance.Sharpness(im).enhance(1.6)

    # Cap resolution — this is a web avatar, not a print asset.
    max_dim = 1200
    if max(im.size) > max_dim:
        im.thumbnail((max_dim, max_dim), Image.LANCZOS)

    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "JPEG", quality=92, optimize=True)
    print(f"Saved enhanced photo to {dst} ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "character_image.png"
    name = sys.argv[2] if len(sys.argv) > 2 else "profile.jpg"
    enhance(src, OUT_DIR / name)
