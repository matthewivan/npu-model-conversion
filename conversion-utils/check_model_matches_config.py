#!/usr/bin/env python3
"""
check_model_matches_config.py — stop the conversion if the .pt doesn't match model_convert_config.yaml.

These mistakes all produce a .rknn without any error, so they have to be caught here:
  - 'data' points at a dataset with different classes than the model was trained on
  - 'imgsz' differs from the size the model was trained at

Set SKIP_MODEL_CHECKS=1 when the difference is intentional.
"""
import os
import sys

import torch
import ultralytics
import yaml

CFG = os.environ.get("CFG_FILE", "model_convert_config.yaml")

def as_name_list(names) -> list:
    if isinstance(names, dict):
        return [names[k] for k in sorted(names)]
    return list(names)

def as_height_width(imgsz) -> list:
    if isinstance(imgsz, int):
        return [imgsz, imgsz]
    return list(imgsz) * 2 if len(imgsz) == 1 else list(imgsz)

def load_checkpoint(model_pt: str) -> dict:
    if not os.path.isfile(model_pt):
        print(f"ERROR: model file '{model_pt}' not found", file=sys.stderr)
        sys.exit(1)
    try:
        return torch.load(model_pt, map_location="cpu")
    except (AttributeError, ModuleNotFoundError) as e:
        print(f"ERROR: '{model_pt}' can't be loaded by the bundled Ultralytics {ultralytics.__version__}. "
              f"Only YOLOv8 models are supported. ({e})", file=sys.stderr)
        sys.exit(1)

def main():
    with open(CFG, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    model_pt = cfg.get("model")
    data_yaml = cfg.get("data")
    imgsz = cfg.get("imgsz")

    ckpt = load_checkpoint(model_pt)
    model = ckpt.get("ema") or ckpt.get("model")
    errors = []

    # fp models aren't calibrated, so 'data' isn't used and can't affect the result
    if cfg.get("precision") != "fp" and data_yaml and os.path.isfile(data_yaml):
        with open(data_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        model_names = as_name_list(model.names)
        data_names = as_name_list(data.get("names", []))
        if model_names != data_names:
            errors.append(f"classes in '{model_pt}' don't match '{data_yaml}':\n"
                          f"    model ({len(model_names)}): {model_names}\n"
                          f"    data  ({len(data_names)}): {data_names}")

    train_imgsz = ckpt.get("train_args", {}).get("imgsz")
    if train_imgsz is None:
        print(f"WARNING: '{model_pt}' doesn't record its training image size, skipping the imgsz check")
    elif imgsz is not None and as_height_width(train_imgsz) != as_height_width(imgsz):
        errors.append(f"imgsz in {CFG} is {imgsz}, but '{model_pt}' was trained at {train_imgsz}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("Fix model_convert_config.yaml, or run with SKIP_MODEL_CHECKS=1 if this is intentional.", file=sys.stderr)
        sys.exit(1)

    print(f"Model matches config (imgsz={imgsz}).")

if __name__ == "__main__":
    main()
