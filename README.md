# Tiny_Test_A - Building Type Classification (Tiny Research Test)

Notebook-first (with a CLI wrapper) pipeline to train and evaluate multiple transfer-learning vision models to classify **building type** from **Google Street View-style** images.

## What's in this project

**Goal:** predict a building-type label for a location based on its street-view images.

**Classes (fixed):**
`single_family`, `apartment_condo`, `commercial`, `mixed_use`, `empty_land`, `unknown`

**Models trained (torchvision):**
ResNet50, EfficientNet-B0, VGG16, MobileNet-V2, ViT-B/16 (`vit_b_16`)

**Key outputs (written to `./results/` by default):**
- `predictions.csv` (final predictions)
- `intermediate_results.jsonl` (per-image probabilities + metadata)
- `best_model.txt`
- `variation_experiment_report.txt`
- `error_analysis_report.md`
- `metrics/` (confusion matrices, comparison tables, etc.)
- `plots/` (training curves and summary plots)
- `gradcam/` (GradCAM visualizations)

## Dataset

Default dataset path in the notebook:
`revised_gsv_dataset_tiny_test/data`

This tiny dataset contains **10 locations** in Charlotte, NC with **104 images** total (2007-2024). See:
`revised_gsv_dataset_tiny_test/data/metadata.md`

## Results (latest run)

From `results/best_model.txt` (timestamp `2026-03-17T22:58:15`):
- **Best model:** `vgg16`
- **Test F1-macro:** `0.5000`

Notes:
- The test set contains **8 test samples** in this run (see `results/error_analysis_report.md`).
- Accuracy can be high while macro-F1 is lower because macro-F1 averages across all 6 classes (including classes with no support in this tiny split).

Augmentation ablation (baseline vs no augmentation), from `results/variation_experiment_report.txt` (generated `2026-03-17 22:59:37`):
- F1-macro: `0.5000 -> 0.4028`
- Accuracy: `1.0000 -> 0.7500`
- Prediction agreement: `75%` (6/8 same)

Error analysis, from `results/error_analysis_report.md` (generated `2026-03-17 23:00:30`):
- Model: `vgg16`
- Challenging cases: `1/8` (failure mode: `ambiguous`)

## How to run (recommended: Jupyter)

1. Create + activate a venv (PowerShell, from `Tiny_Test_A/`):

   `python -m venv .venv`

   `.\\.venv\\Scripts\\Activate.ps1`

2. Install packages (see "Packages to install" below).
3. Start Jupyter and run the notebook top-to-bottom:

   `jupyter notebook`

   Open: `setup_configuration.ipynb`

### Configure paths

You can either edit the notebook variables:
- `DATA_PATH` (dataset `data/` folder)
- `OUTPUT_DIR` (where `results/` are written)

...or set environment variables (useful for CLI execution):
- `PIPELINE_DATA_PATH` (points to the dataset `data/` folder, or its parent dataset root)
- `PIPELINE_OUTPUT_DIR` (output directory)

## How to run via CLI (`run_pipeline.py`)

`run_pipeline.py` executes the notebook using `jupyter nbconvert --execute`, and passes configuration via env vars.

From `Tiny_Test_A/`:

`python run_pipeline.py --data-path .\\revised_gsv_dataset_tiny_test --output-dir .\\results`

Optional:
- `--notebook setup_configuration.ipynb`
- `--kernel tiny_test_a_venv`
- `--executed-notebook .\\results\\executed_setup_configuration.ipynb`

## Packages to install

Minimum set used by the notebook:
- `torch`, `torchvision`, `torchaudio`
- `pandas`, `numpy`
- `pillow`
- `matplotlib`, `seaborn`
- `scikit-learn`
- `tqdm`
- `opencv-python`
- `grad-cam` (PyTorch Grad-CAM / `pytorch_grad_cam`)
- `jupyter`, `nbconvert`, `ipykernel`

Install (CPU-only example):

`pip install torch torchvision torchaudio`

`pip install pandas numpy pillow matplotlib seaborn scikit-learn tqdm opencv-python grad-cam jupyter nbconvert ipykernel`

If you want GPU/CUDA wheels, install PyTorch using the selector for your CUDA version (the notebook contains an example for CUDA 11.8).

## Repo layout (important files)

- `setup_configuration.ipynb`: main end-to-end pipeline (data prep -> train -> eval -> reports)
- `run_pipeline.py`: CLI wrapper to execute the notebook
- `revised_gsv_dataset_tiny_test/data/`: tiny dataset (images + metadata)
- `results/`: outputs from the latest execution (reports, metrics, plots, GradCAM)
