# Video Summary Tool

A highly efficient, Python-based video summary tool that leverages YOLO for object detection and SORT for tracking. It allows for real-time analysis and insights, detecting and logging selected objects within the video, saving screenshots of key scenes, and generating a visual report.

> **Processing Speed**: This tool processes video approximately **4x faster than real-time** on supported hardwares using nano model.

---

## Features
- **Real-Time Detection**: Detects and tracks specified objects throughout the video.
- **Critical Scene Capture**: Automatically saves screenshots when new objects appear.
- **Visual Reporting**: Generates a log and graphical report on detected entities over time.

## Requirements
- Python 3.x
- CUDA-supported NVIDIA GPU (for accelerated processing with PyTorch)
- Libraries:
  - `customtkinter`
  - `torch` (only required if using a GPU with CUDA)
  - `ultralytics`
  - `opencv-python`
  - `Pillow`
  - `cvzone`
  - `numpy`
  - `sort` (for tracking)
  - `seaborn`
  - `matplotlib`

## Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/elBo3Bo3/Video-Summary-Tool.git
    cd Video-Summary-Tool
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Install PyTorch (optional, only if using an NVIDIA GPU):
   - You can install with:
     ```bash
     pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
     ```
     Replace `cu1124` with the appropriate CUDA version for your setup. [Refer to PyTorch documentation](https://pytorch.org/get-started/locally/) for detailed installation options.

## Usage
To run the application with the GUI:
```bash
python app.py
```
- **Upload a Video**

- **Select Object Classes**: Choose specific object classes to detect and track.

- **Run Analysis**: Click Start to begin processing the video.

- **Note**: Processing with nano model runs at about 4x the video’s actual duration on compatible hardware. Larger models requires more processing time.

## Output
- **Log File**: Provides a timestamped list of detected objects.
- **Screenshots**: Saved for each critical scene in the history directory.
- **Visual Report**: A graph of object counts over time.

## Demo
![Demo](demo.gif)
## Acknowledgments
- Built with [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) and the [SORT](https://github.com/abewley/sort) tracking algorithm.
- Optimized for PyTorch with CUDA support for high-performance computing
