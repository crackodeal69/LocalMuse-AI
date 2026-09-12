# LocalMuse Environment and Models

This file is the handoff map for future agents and setup work.

## Project Root

```text
E:\AI\LocalMuse-AI
```

Keep project-owned models, datasets, outputs, and experiment records under this
root or another explicitly documented folder on drive `E:`.

## Current Runtime

The working Python runtime is currently reused from the existing LoRA setup:

```text
E:\ai_work\kohya_ss\.venv\Scripts\python.exe
```

Verified on 2026-09-12:

- GPU: NVIDIA GeForce RTX 3080
- CUDA available: yes
- PyTorch: 2.7.0+cu128
- transformers: 4.54.1
- accelerate: 1.8.1

Do not move this virtual environment casually. Windows virtual environments can
contain absolute paths and it is shared with the older kohya_ss workflow. A future
installer may create a clean LocalMuse environment after the model pipeline is
stable.

## Models

### Caption model

```text
Model: microsoft/Florence-2-large
Purpose: image caption generation for LoRA dataset preparation
Location: E:\AI\LocalMuse-AI\models\huggingface
Approximate size: 1.45 GB
```

The model is loaded with `trust_remote_code=True`, eager attention, FP16 on CUDA,
and `use_cache=False` because this combination is compatible with the current
Transformers version.

### Existing LoRA checkpoints

These belong to the older AI work area and are not yet part of the LocalMuse
pipeline:

```text
E:\ai_work\models\Lora
```

Move or copy them only after confirming which base model and training run they
belong to.

### LocalMuse baseline checkpoint

The verified RealVisXL checkpoint used by the previous `sid_person` run is copied
to the LocalMuse model area:

```text
E:\AI\LocalMuse-AI\models\base\realvisxlV50_v50Bakedvae.safetensors
```

The first LocalMuse training configuration is:

```text
E:\AI\LocalMuse-AI\configs\lora_baseline_dataset_v01.toml
```

## Dataset

Current pilot dataset:

```text
E:\AI\LocalMuse-AI\data\nag_person
```

It contains 30 PNG images and generated sidecar captions. Each image has a
same-name `.txt` file beginning with the trigger token `nag_person`.

## Caption Generation

Run from the project root:

```powershell
$env:HF_HOME = 'E:\AI\LocalMuse-AI\models\huggingface'
& 'E:\ai_work\kohya_ss\.venv\Scripts\python.exe' -m tools.generate_captions `
  'E:\AI\LocalMuse-AI\data\nag_person' `
  --trigger nag_person `
  --cache-dir 'E:\AI\LocalMuse-AI\models\huggingface'
```

The CLI defaults to the project model directory, so `--cache-dir` and `HF_HOME`
can be omitted after confirming the runtime's Hugging Face configuration.

Clean generated captions without loading the model again:

```powershell
python -m tools.clean_captions `
  'E:\AI\LocalMuse-AI\data\nag_person' `
  --trigger nag_person
```

The cleanup removes speculative, identity-related, and subjective text while
keeping visible details such as clothing, pose, and background.

## Rules for Future Agents

- Do not download duplicate copies into `E:\ai_work`.
- Do not commit model weights, generated captions, or private source photos.
- Before adding a model, record its name, purpose, exact location, size, and
  runtime requirements here.
- Keep caption generation, LoRA training, evaluation, and image generation as
  separate components.