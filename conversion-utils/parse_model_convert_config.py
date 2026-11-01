#!/usr/bin/env python3
import os, sys, yaml

CFG = os.environ.get("CFG_FILE", "model_convert_config.yaml")
with open(CFG, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f) or {}

model_pt = cfg.get("model")
data_yaml = cfg.get("data")
conversion_target = cfg.get("target")
conversion_precision = cfg.get("precision")
subset_interval = cfg.get("subset_interval")

# Calibration images are only needed for quantized (i8/u8) models
needs_dataset = conversion_precision != "fp"

required = {"model": model_pt, "target": conversion_target, "precision": conversion_precision}
if needs_dataset:
    required.update({"data": data_yaml, "subset_interval": subset_interval})

missing = [key for key, value in required.items() if value in (None, "")]
if missing:
    print(f"ERROR: {', '.join(missing)} not found in {CFG}", file=sys.stderr)
    sys.exit(1)

if needs_dataset and not os.path.isfile(data_yaml):
    print(f"ERROR: data file '{data_yaml}' not found", file=sys.stderr)
    sys.exit(1)

# Normalize
model_pt = os.path.normpath(model_pt)
data_yaml = os.path.normpath(data_yaml) if data_yaml else ""
conversion_target = os.path.normpath(conversion_target)
conversion_precision = os.path.normpath(conversion_precision)
subset_interval = "" if subset_interval is None else os.path.normpath(str(subset_interval))

model_dir  = os.path.normpath(os.path.dirname(model_pt) or ".")
model_stem = os.path.splitext(os.path.basename(model_pt))[0]
onnx_path  = os.path.join(model_dir, f"{model_stem}.onnx")
rknn_path  = os.path.join(model_dir, f"{model_stem}_{conversion_target}.rknn")

def resolve_split(data: dict, dataset_root: str, key: str, default_dirs: list[str]) -> str:
    """Return a split's images folder, trying data.yaml's path first (same rules as Ultralytics)."""
    value = data.get(key)
    if isinstance(value, list):
        value = value[0] if value else None

    candidates = []
    if value:
        root = os.path.join(dataset_root, str(data.get("path") or ""))
        candidates.append(os.path.join(root, value))
        if value.startswith("../"):
            candidates.append(os.path.join(root, value[3:]))
    candidates += [os.path.join(dataset_root, d) for d in default_dirs]

    for candidate in candidates:
        if os.path.isdir(candidate):
            return os.path.normpath(candidate)
    return os.path.normpath(candidates[0])

train_images = valid_images = test_images = ""
if data_yaml and os.path.isfile(data_yaml):
    with open(data_yaml, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Dataset root = folder containing data.yaml
    dataset_root = os.path.dirname(os.path.abspath(data_yaml))

    train_images = resolve_split(data, dataset_root, "train", ["train/images", "images/train"])
    valid_images = resolve_split(data, dataset_root, "val", ["valid/images", "val/images", "images/val"])
    test_images  = resolve_split(data, dataset_root, "test", ["test/images", "images/test"])

def sh_escape(s: str) -> str:
    return "'" + s.replace("'", "'\"'\"'") + "'"

print(f"MODEL_PT={sh_escape(model_pt)}")
print(f"DATA_YAML={sh_escape(data_yaml)}")
print(f"CONVERSION_TARGET={sh_escape(conversion_target)}")
print(f"CONVERSION_PRECISION={sh_escape(conversion_precision)}")
print(f"SUBSET_INTERVAL={sh_escape(subset_interval)}")
print(f"MODEL_DIR={sh_escape(model_dir)}")
print(f"MODEL_STEM={sh_escape(model_stem)}")
print(f"ONNX_PATH={sh_escape(onnx_path)}")
print(f"RKNN_PATH={sh_escape(rknn_path)}")
print(f"TRAIN_IMAGES_DIR={sh_escape(train_images)}")
print(f"VAL_IMAGES_DIR={sh_escape(valid_images)}")
print(f"TEST_IMAGES_DIR={sh_escape(test_images)}")

