# NPU Model Conversion Guide
1. move/copy your .pt model into `models/`
2. move/copy your YOLOv8 dataset (should have data.yaml and train, test, valid images) into `datasets/`
3. modify `model`, `data`, and `imgsz` in `modelTrainConfig.yaml`
4. run `chmod +x converter.sh`
5. run `./converter.sh`
6. your .rknn model should pop up in `models/`
