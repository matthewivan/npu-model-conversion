# NPU Model Conversion Guide

1. **Add your dataset**
   - Move or copy your **YOLOv8 dataset folder** into the `datasets/` directory.  
   - This folder **must contain**:
     - `data.yaml`
     - `train/`, `valid/`, and `test/` subfolders

2. **Get your YOLOv8 `.pt` model**
   - **If you already have a trained model**:  
     - Move or copy your `.pt` file into the `models/` folder.
   - **If you need to train a model**:
     1. Edit `modelTrainConfig.yaml` and set:
        - `model`
        - `data`
        - `imgsz`
     2. From the repository’s **top-level directory**, run:
        ```bash
        chmod +x train_custom_yolo_model
        ./train_custom_yolo_model
        ```
     3. After training, move the `.pt` file from the latest `runs/detect` folder to the `models/` folder. (The command line will show its exact location.)

3. **Prepare the conversion script**
   - From the repository’s **top-level directory**, run:
     ```bash
     chmod +x convert_yolo_to_rknn
     ```

4. **Convert YOLO to RKNN**
   - Still in the top-level directory, run:
     ```bash
     ./convert_yolo_to_rknn
     ```

5. **Find your RKNN model**
   - The generated `.rknn` file will appear in the `models/` folder.
