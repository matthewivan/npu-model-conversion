# Environment Setup
1. **Install conda**
   - Follow this guide: https://github.com/conda-forge/miniforge
2. **Create a conda virtual environment**
   - ```bash
     conda create -n rknn-311 python=3.11
     ```
3. **Activate conda environment**
   - ```bash
     conda activate rknn-311
     ```
4. **Setup environment**
   - Run this command to install all the necessary pip packages and RKNN-Toolkit2 library:
     ```bash
     chmod +x setup_conda_environment
     ./setup_conda_environment
     ```

# NPU Model Conversion Guide

0. **Configure keys in `model_convert_config.yaml` with the appropriate values**
   Paths should be relative to the repository's **top-level directory** (e.g. `datasets/GMU_Dataset/data.yaml`)
   ``` yaml
     # Required for training a custom YOLOv8 model
     data: datasets/your_dataset_folder/data.yaml   # YOLO data config file
     epochs: 100                                    # (int) number of epochs to train for
     batch: 16                                      # (int) number of images per batch (-1 for AutoBatch)
     imgsz: 640                                     # (int | list) input images size as int for train and val modes, or list[h,w] for predict and export modes
     cache: False                                   # (bool) True/ram, disk or False. Use cache for data loading
     device: 0                                      # (int | str | list, optional) device to run on, i.e. cuda device=0 or device=0,1,2,3 or device=cpu
   
     # Required for conversion (YOLOv8 .pt to .rknn)
     target: rk3566                                 # your specific NPU target chip
     precision: i8                                  # e.g., i8 / fp
     subset_interval: 5                             # how often to sample images for calibration
     model: models/your_model.pt                    # path to your trained YOLOv8 .pt file
     data: datasets/your_dataset_folder/data.yaml   # YOLO data config file
     epochs: 100                                    # epochs used for training
     batch: 16                                      # (int) number of images per batch (-1 for AutoBatch)
     imgsz: 640                                     # image size used for training
     cache: False                                   # (bool) True/ram, disk or False. Use cache for data loading
     device: 0                                      # (int | str | list, optional) device to run on, i.e. cuda device=0 or device=0,1,2,3 or device=cpu
     ```

2. **Add your dataset**
   - Move or copy your **YOLOv8 dataset folder** into the `datasets/` directory.  
   - This folder **must contain**:
     - `data.yaml`
     - `train/`, `valid/`, and `test/` subfolders
   - Edit `model_convert_config.yaml` and set:
     - `data` (e.g. `data: datasets/GMU_Dataset/data.yaml`)

3. **Get your YOLOv8 `.pt` model**
   - **If you already have a trained model**:  
     1. Move or copy your `.pt` file into the `models/` folder.
   - **If you need to train a model**:
     1. Edit `model_convert_config.yaml` and set:
        - `epochs`
        - `batch`
        - `imgsz`
        - `cache`
        - `device` (set to `cpu` if training and/or converting without an NVIDIA GPU)
     2. From the repository’s **top-level directory**, run:
        ```bash
        chmod +x train_custom_yolo_model
        ./train_custom_yolo_model
        ```
     3. After training, move the `.pt` file from the latest `runs/detect` folder to the `models/` folder. (The command line will show its exact location. The folder should contain best.pt and last.pt)

4. **Prepare the conversion script**
   -  Edit `model_convert_config.yaml` and set:
        - `model` (e.g. `model: models/GMU_yolov8n.pt`)
        - `target`
        - `precision`
        - `subset_interval`
   - From the repository’s **top-level directory**, run:
     ```bash
     chmod +x convert_yolo_to_rknn
     ```

5. **Convert YOLO to RKNN**
   - Still in the top-level directory, run:
     ```bash
     ./convert_yolo_to_rknn
     ```

6. **Find your RKNN model**
   - The generated `.rknn` file will appear in the `models/` folder with the same name as your `.pt` model.
