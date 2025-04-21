#!/bin/bash

echo "Exporting PyTorch model to ONNX..."
bash ./conversion-utils/export_to_onnx.sh

echo "Running RKNN Toolkit 2 setup..."
bash ./conversion-utils/rknn-toolkit2-setup.sh

echo "Exporting ONNX model to RKNN..."
bash ./conversion-utils/export_to_rknn.sh

echo "Done."
