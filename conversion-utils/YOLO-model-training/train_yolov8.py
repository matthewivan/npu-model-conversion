from pathlib import Path
import os
import yaml
from ultralytics import YOLO

CFG_FILE = "model_convert_config.yaml"

def resolve_cfg_value(cfg_path: str, key: str):
    """Read `key` from YAML and resolve paths if appropriate."""
    p = Path(cfg_path)
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    if key not in cfg or cfg[key] is None:
        raise ValueError(f"'{key}' not found in {cfg_path}")

    value = cfg[key]

    # Only resolve if value looks like a path (string with /, \, or .)
    if isinstance(value, str) and ("/" in value or "\\" in value or "." in value):
        resolved = Path(os.path.expandvars(os.path.expanduser(value)))
        if not resolved.is_absolute():
            resolved = (p.parent / resolved).resolve()
        return resolved

    # Otherwise return as-is (numbers, bools, etc.)
    return value


# Pull values from model_convert_config.yaml
model_path = resolve_cfg_value(CFG_FILE, "base_model")
data_path = resolve_cfg_value(CFG_FILE, "data")
train_epochs = resolve_cfg_value(CFG_FILE, "epochs")
train_batch = resolve_cfg_value(CFG_FILE, "batch")
train_imgsz = resolve_cfg_value(CFG_FILE, "imgsz")
train_cache = resolve_cfg_value(CFG_FILE, "cache")
train_device = resolve_cfg_value(CFG_FILE, "device")

# Train
model = YOLO(str(model_path))
model.train(
    data=str(data_path),
    epochs=train_epochs,
    batch=train_batch,
    imgsz=train_imgsz,
    cache=train_cache,
    device=str(train_device),
)

