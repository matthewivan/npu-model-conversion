#!/usr/bin/env python3
import os, sys, yaml

CFG = os.environ.get("CFG_FILE", "model_convert_config.yaml")
with open(CFG, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f) or {}

model_pt = cfg.get("model")
data_yaml = cfg.get("data")
conversion_target = cfg.get("target")
conversion_precision = cfg.get("precision")
subset_interval = str(cfg.get("subset_interval"))

if not model_pt or not data_yaml or not conversion_target or not conversion_precision or not subset_interval:
    print("echo 'ERROR: model/data not found in YAML'", file=sys.stderr)
    sys.exit(1)

# Normalize
model_pt = os.path.normpath(model_pt)
data_yaml = os.path.normpath(data_yaml)
conversion_target = os.path.normpath(conversion_target)
conversion_precision = os.path.normpath(conversion_precision)
subset_interval = os.path.normpath(subset_interval)

model_dir  = os.path.normpath(os.path.dirname(model_pt) or ".")
model_stem = os.path.splitext(os.path.basename(model_pt))[0]
onnx_path  = os.path.join(model_dir, f"{model_stem}.onnx")
rknn_path  = os.path.join(model_dir, f"{model_stem}.rknn")

# Dataset root = folder containing data.yaml
data_yaml_abs = os.path.abspath(data_yaml)
dataset_root  = os.path.dirname(data_yaml_abs)

train_images = os.path.join(dataset_root, "train", "images")
valid_images = os.path.join(dataset_root, "valid", "images")
test_images  = os.path.join(dataset_root, "test",  "images")

# Fallback for some configs that use 'val/' instead of 'valid/'
if not os.path.isdir(valid_images):
    valid_images = os.path.join(dataset_root, "val", "images")

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

