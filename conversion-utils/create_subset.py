#!/usr/bin/env python3
"""
pick_images.py — write selected image paths to a .txt file.

Examples:
  # Write every 5th image (5, 10, 15, ...) by name:
  python pick_images.py /path/to/folder output.txt --n 5 --mode every_n --sort name

  # Write the image after each 5-image block (6, 11, 16, ...) recursively:
  python pick_images.py /path/to/folder output.txt --n 5 --mode after_every_n --recursive

  # Strip everything before 'datasets/' so output starts after it:
  python pick_images.py /path/to/folder output.txt --n 5 --strip-after datasets
"""
from pathlib import Path
import argparse
import sys

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp", ".heic", ".heif"}

def collect_images(folder: Path, recursive: bool) -> list[Path]:
    if recursive:
        files = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    else:
        files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    return files

def sort_images(files: list[Path], sort_key: str) -> list[Path]:
    if sort_key == "name":
        return sorted(files, key=lambda p: p.name.lower())
    elif sort_key == "mtime":
        return sorted(files, key=lambda p: p.stat().st_mtime)
    else:
        return files

def select_indices(total: int, n: int, mode: str) -> list[int]:
    """
    Return 0-based indices of selected images.
    - 'every_n': selects n, 2n, 3n, ... (1-based) => 0-based: n-1, 2n-1, ...
    - 'after_every_n': selects n+1, 2n+1, 3n+1, ... (1-based) => 0-based: n, 2n, ...
    """
    indices = []
    if mode == "every_n":
        k = n
        while k <= total:
            indices.append(k - 1)
            k += n
    elif mode == "after_every_n":
        k = n + 1
        while k <= total:
            indices.append(k - 1)
            k += n
    else:
        raise ValueError("Unknown mode")
    return indices

def strip_after_component(path: Path, marker: str) -> str:
    """
    Return the subpath after the first occurrence of directory `marker`.
    Case-insensitive match on each path component. If marker not found,
    return empty string (caller can fallback).
    """
    marker_lower = marker.lower()
    parts = list(path.parts)
    for i, part in enumerate(parts):
        if part.lower() == marker_lower:
            tail = parts[i+1:]
            return "/".join(tail)  # POSIX-style in txt, even on Windows
    return ""

def main():
    ap = argparse.ArgumentParser(description="Write selected image paths to a .txt file.")
    ap.add_argument("folder", type=Path, help="Folder containing images")
    ap.add_argument("output", type=Path, help="Output .txt file path")
    ap.add_argument("--n", type=int, required=True, help="Interval n")
    ap.add_argument("--mode", choices=["every_n", "after_every_n"], default="every_n",
                    help="Selection mode: 'every_n' (n,2n,3n,...) or 'after_every_n' (n+1,2n+1,...)")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument("--sort", choices=["name", "mtime"], default="name", help="Sort order before selecting")
    ap.add_argument("--abs", action="store_true", help="Write absolute paths (default: relative)")
    ap.add_argument("--strip-after", type=str, default="datasets",
                    help="Directory name to strip everything before it (default: 'datasets'). "
                         "Output starts right after this directory. Case-insensitive.")
    args = ap.parse_args()

    if args.n <= 0:
        print("Error: --n must be a positive integer.", file=sys.stderr)
        sys.exit(2)

    folder = args.folder
    if not folder.exists() or not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory.", file=sys.stderr)
        sys.exit(2)

    files = collect_images(folder, args.recursive)
    if not files:
        print("No images found.", file=sys.stderr)
        args.output.write_text("")
        sys.exit(0)

    files = sort_images(files, args.sort)
    indices = select_indices(len(files), args.n, args.mode)
    selected = [files[i] for i in indices]

    base = folder.resolve()

    lines: list[str] = []
    for p in selected:
        resolved = p.resolve()

        # Preferred: strip everything up to the marker (e.g., 'datasets')
        stripped = strip_after_component(resolved, args.strip_after) if args.strip_after else ""
        if stripped:
            # If the stripped tail doesn't include 'images' part and you only want filename:
            # stripped = stripped.split('/')[-1]
            lines.append(stripped)
            continue

        # Fallback to original behavior if marker not found
        if args.abs:
            lines.append(str(resolved))
        else:
            try:
                rel = resolved.relative_to(base)
            except ValueError:
                rel = resolved  # if on another drive, etc.
            lines.append(str(rel).replace("\\", "/"))

    # Ensure parent directories exist for output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"Wrote {len(lines)} paths to '{args.output}' out of {len(files)} images.")

if __name__ == "__main__":
    main()

