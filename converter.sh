#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=./
CFG_FILE="modelTrainConfig.yaml"

# --- Read YAML and export variables: MODEL_PT, DATA_YAML, MODEL_DIR, MODEL_STEM, ONNX_PATH, RKNN_PATH,
#     TRAIN_IMAGES_DIR, VAL_IMAGES_DIR, TEST_IMAGES_DIR
eval "$(
python - <<'PYCODE'
import os, sys, yaml

CFG = os.environ.get("CFG_FILE", "modelTrainConfig.yaml")
with open(CFG, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f) or {}

model_pt = cfg.get("model")
data_yaml = cfg.get("data")

if not model_pt or not data_yaml:
    print("echo 'ERROR: model/data not found in YAML'", file=sys.stderr)
    sys.exit(1)

# Normalize
model_pt = os.path.normpath(model_pt)
data_yaml = os.path.normpath(data_yaml)

model_dir  = os.path.normpath(os.path.dirname(model_pt) or ".")
model_stem = os.path.splitext(os.path.basename(model_pt))[0]
onnx_path  = os.path.join(model_dir, f"{model_stem}.onnx")
rknn_path  = os.path.join(model_dir, f"{model_stem}.rknn")

# Dataset root = folder containing data.yaml
data_yaml_abs = os.path.abspath(data_yaml)
dataset_root  = os.path.dirname(data_yaml_abs)

# Expected structure
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
print(f"MODEL_DIR={sh_escape(model_dir)}")
print(f"MODEL_STEM={sh_escape(model_stem)}")
print(f"ONNX_PATH={sh_escape(onnx_path)}")
print(f"RKNN_PATH={sh_escape(rknn_path)}")
print(f"TRAIN_IMAGES_DIR={sh_escape(train_images)}")
print(f"VAL_IMAGES_DIR={sh_escape(valid_images)}")
print(f"TEST_IMAGES_DIR={sh_escape(test_images)}")
PYCODE
)"

echo "Config:"
echo "  MODEL_PT         = $MODEL_PT"
echo "  DATA_YAML        = $DATA_YAML"
echo "  MODEL_DIR        = $MODEL_DIR"
echo "  MODEL_STEM       = $MODEL_STEM"
echo "  ONNX_PATH        = $ONNX_PATH"
echo "  RKNN_PATH        = $RKNN_PATH"
echo "  TRAIN_IMAGES_DIR = $TRAIN_IMAGES_DIR"
echo "  VAL_IMAGES_DIR   = $VAL_IMAGES_DIR"
echo "  TEST_IMAGES_DIR  = $TEST_IMAGES_DIR"
echo

# Full Conversion Flow (.pt to .rknn)

echo "Exporting PyTorch model to ONNX..."
python ./ultralytics/engine/exporter.py

echo "Creating Dataset Samples..."
# Examples: create subsets from any split you want
# python ./conversion-utils/create_subset.py "$TRAIN_IMAGES_DIR" ./datasets/train_subset.txt --n 5 --strip-after datasets
python ./conversion-utils/create_subset.py "$VAL_IMAGES_DIR"   ./datasets/valid_subset.txt --n 5 --strip-after datasets
# python ./conversion-utils/create_subset.py "$TEST_IMAGES_DIR"  ./datasets/test_subset.txt  --n 5 --strip-after datasets

echo "Exporting ONNX model to RKNN..."
python3 ./conversion-utils/convert.py "$ONNX_PATH" rk3566 i8 "$RKNN_PATH"

echo "Done."

