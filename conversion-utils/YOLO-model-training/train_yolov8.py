from pathlib import Path
import os
import yaml
from ultralytics import YOLO

CFG_FILE = "model_convert_config.yaml"

def resolve_cfg_path(cfg_path: str, key: str) -> Path:
    """Read `key` from a YAML file and return an absolute Path."""
    p = Path(cfg_path)
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    if key not in cfg or not cfg[key]:
        raise ValueError(f"'{key}' not found in {cfg_path}")

    raw = str(cfg[key])
    resolved = Path(os.path.expandvars(os.path.expanduser(raw)))
    if not resolved.is_absolute():
        resolved = (p.parent / resolved).resolve()
    return resolved

# Pull values from your training YAML
data_path = resolve_cfg_path(CFG_FILE, "data")
# Pull model from the same YAML config file (falls back to a default if missing)
try:
    model_path = resolve_cfg_path(CFG_FILE, "base_model")
except Exception:
    model_path = Path("./models/yolov8n.pt")

# Train
model = YOLO(str(model_path))
model.train(
    data=str(data_path),
    epochs=100,
    imgsz=640,
    batch=16,
    device="cpu",
    cache=True,
)

