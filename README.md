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

1. **Configure keys in `model_convert_config.yaml` with the appropriate values**

   Paths should be relative to the repository's **top-level directory** (e.g. `datasets/GMU_Dataset/data.yaml`)
   ``` yaml
     # Used for both training and conversion
     data: datasets/your_dataset_folder/data.yaml   # YOLO data config file
     imgsz: 640                                     # (int | list) image size. For conversion, this must match the size your model was trained at
     device: 0                                      # (int | str | list, optional) device to run on, i.e. cuda device=0 or device=0,1,2,3 or device=cpu

     # Required for training a custom YOLOv8 model
     base_model: models/yolov8n.pt                  # pretrained YOLOv8 model to start training from
     epochs: 100                                    # (int) number of epochs to train for
     batch: 16                                      # (int) number of images per batch (-1 for AutoBatch)
     cache: False                                   # (bool) True/ram, disk or False. Use cache for data loading

     # Required for conversion (YOLOv8 .pt to .rknn)
     model: models/your_model.pt                    # path to your trained YOLOv8 .pt file
     target: rk3566                                 # your specific NPU target chip
     precision: i8                                  # e.g., i8 / fp
     subset_interval: 5                             # how often to sample images for calibration
     ```

2. **Add your dataset**
   - Move or copy your **YOLOv8 dataset folder** into the `datasets/` directory.
   - This folder **must contain** `data.yaml`, and the `train` and `val` paths in `data.yaml` must point to your image folders (e.g. `valid/images`, or `images/val`).
   - Image filenames can't contain spaces, because RKNN-Toolkit2 treats a space in the calibration list as a separator.
   - Edit `model_convert_config.yaml` and set:
     - `data` (e.g. `data: datasets/GMU_Dataset/data.yaml`)
   - If you only have a `.pt` model and no dataset, set `precision: fp` and skip this step. Quantized models (`i8`) need calibration images.

3. **Get your YOLOv8 `.pt` model**
   - Only YOLOv8 models are supported. Conversion uses the Ultralytics version bundled in this repository, which can't load newer architectures such as YOLO11.
   - **If you already have a trained model**:
     1. Move or copy your `.pt` file into the `models/` folder.
   - **If you need to train a model**:
     1. Edit `model_convert_config.yaml` and set:
        - `base_model`
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
     3. After training, move `best.pt` from the `weights` folder printed at the end of training to the `models/` folder, and give it a unique name so the next model doesn't overwrite it.

4. **Prepare the conversion script**
   - Edit `model_convert_config.yaml` and set:
     - `model` (e.g. `model: models/GMU_yolov8n.pt`)
     - `target`
     - `precision`
     - `subset_interval`
   - Check that `data` and `imgsz` still match this model.
   - From the repository’s **top-level directory**, run:
     ```bash
     chmod +x convert_yolo_to_rknn
     ```

5. **Convert YOLO to RKNN**
   - Still in the top-level directory, run:
     ```bash
     ./convert_yolo_to_rknn
     ```
   - The conversion stops if the model's class names don't match `data.yaml`, or if `imgsz` differs from the size the model was trained at. If the difference is intentional (e.g. calibrating a pretrained COCO model on your own images), run:
     ```bash
     SKIP_MODEL_CHECKS=1 ./convert_yolo_to_rknn
     ```

6. **Find your RKNN model**
   - The generated `.rknn` file will appear in the `models/` folder as `<model name>_<target>.rknn` (e.g. `GMU_yolov8n_rk3566.rknn`). Converting the same model for the same target again overwrites it.

# Test NPU Model

1. git clone https://github.com/matthewivan/rknn-npu-setup.git

2. follow the instructions to setup the rknn npu. Use a `librknnrt.so` version that matches the RKNN-Toolkit2 version used for conversion (2.3.2). The sample output below shows the warning you get when they differ.

3. copy a couple images from `npu-model-conversion/datasets/your_dataset_name/test/` into `rknn-npu-setup/npu_inference_test/images/`.

4. copy your `.rknn` model into `rknn-npu-setup/npu_inference_test/cv_models/`, then edit these values in the `detect_from_image.py` python script:
   - `CLASSES`: your class names from `npu-model-conversion/datasets/your_dataset_name/data.yaml`, in the same order
   - `IMG_SIZE`: the `imgsz` you converted with (e.g. `(640, 640)`)
   - `model_path`: the path to your `.rknn` model
   - `target`: the `target` you converted for

5. run `python detect_from_image.py` and the results should look something like this:

```bash
--> Init runtime environment
I RKNN: [20:59:48.753] RKNN Runtime Information, librknnrt version: 2.0.0b0 (35a6907d79@2024-03-24T10:31:14)
I RKNN: [20:59:48.754] RKNN Driver Information, version: 0.8.8
I RKNN: [20:59:48.756] RKNN Model Information, version: 6, toolkit version: 2.3.2(compiler version: 2.3.2 (e045de294f@2025-04-07T19:48:25)), target: RKNPU lite, target platform: rk3566, framework name: ONNX, framework layout: NCHW, model inference type: static_shape
W RKNN: [20:59:48.756] RKNN Model version: 2.3.2 not match with rknn runtime version: 2.0.0
done
inference time: 0.2333758630002194
IMG: 20250318_165124_497413_jpg.rf.4b72946db1c1a022c29a8e7d0d4f8242.jpg
Blue Buoy @ (290 225 330 280) 0.875
Blue Buoy: 0.875213623046875
Detection result save to ./result/20250318_165124_497413_jpg.rf.4b72946db1c1a022c29a8e7d0d4f8242.jpg


inference time: 0.185511638999742
IMG: 20250318_165131_262919_jpg.rf.0df12e1db2c6d614975e1fb0081f0b66.jpg
Blue Buoy @ (553 255 617 331) 0.890
Or @ (227 244 263 280) 0.813
Blue Buoy: 0.8902873992919922
Or: 0.8134765625
Detection result save to ./result/20250318_165131_262919_jpg.rf.0df12e1db2c6d614975e1fb0081f0b66.jpg


inference time: 0.20892454100021496
IMG: 20250318_165150_927184_jpg.rf.a28d01b9342c2e68935b1ffad0aad1d7.jpg
Blue Buoy @ (0 0 51 359) 0.823
Blue Buoy: 0.8234366178512573
Detection result save to ./result/20250318_165150_927184_jpg.rf.a28d01b9342c2e68935b1ffad0aad1d7.jpg


inference time: 0.17595874700009517
IMG: 20250318_165212_124905_jpg.rf.15a763e7f8a6bae3bba65344664cc394.jpg
Blue Buoy @ (374 139 472 309) 0.916
Blue Buoy: 0.9163627624511719
Detection result save to ./result/20250318_165212_124905_jpg.rf.15a763e7f8a6bae3bba65344664cc394.jpg


inference time: 0.1777564409999286
IMG: 20250318_170212_167080_jpg.rf.ca712bba36268dc9fb871442252f525c.jpg
Black Buoy @ (509 191 592 260) 0.909
Black Buoy: 0.9089126586914062
Detection result save to ./result/20250318_170212_167080_jpg.rf.ca712bba36268dc9fb871442252f525c.jpg


inference time: 0.1829018769999493
IMG: 20250318_170651_326692_jpg.rf.6dad741ac6771bc84a88cf04d64870a2.jpg
Maroon Buoy @ (603 63 640 308) 0.708
Or @ (237 195 287 235) 0.370
Or @ (254 199 282 230) 0.265
Maroon Buoy: 0.7077598571777344
Or: 0.37042236328125
Or: 0.265106201171875
Detection result save to ./result/20250318_170651_326692_jpg.rf.6dad741ac6771bc84a88cf04d64870a2.jpg


inference time: 0.1703153939997719
IMG: 20250318_170651_889563_jpg.rf.bc1fb0a979a8a8a1c42b3ee2ab0d10c6.jpg
Maroon Buoy @ (539 148 640 363) 0.862
Or @ (166 230 195 263) 0.734
Maroon Buoy: 0.8619149923324585
Or: 0.73358154296875
Detection result save to ./result/20250318_170651_889563_jpg.rf.bc1fb0a979a8a8a1c42b3ee2ab0d10c6.jpg


inference time: 0.1721346729996185
IMG: 20250318_170901_764366_jpg.rf.f87b989c36c4d364451c30c52b14d01c.jpg
Orange Buoy @ (432 191 481 266) 0.816
Orange Buoy: 0.8157863616943359
Detection result save to ./result/20250318_170901_764366_jpg.rf.f87b989c36c4d364451c30c52b14d01c.jpg


inference time: 0.17895558500003972
IMG: GMUphoto16_jpg.rf.aac64671ff2915a0b1e4e163c76d3109.jpg
Maroon Buoy @ (80 0 159 70) 0.400
Maroon Buoy: 0.4001747965812683
Detection result save to ./result/GMUphoto16_jpg.rf.aac64671ff2915a0b1e4e163c76d3109.jpg


inference time: 0.17094048900025882
IMG: GMUphoto2320_jpg.rf.a965e2290557be4058be55ef58fdae0f.jpg
Detection result save to ./result/GMUphoto2320_jpg.rf.a965e2290557be4058be55ef58fdae0f.jpg

```