# LocalMuse AI: Current Handoff

Last updated: 2026-09-13

## What This Project Is

LocalMuse is a local Windows application for preparing a personal image dataset,
captioning it, training a LoRA, and generating images through an easier UI than
raw Forge. Forge remains the generation backend for now.

## Current URLs and Launch

Start the development stack with one double-click:

```text
E:\AI\LocalMuse-AI\scripts\start_localmuse.bat
```

Then open:

```text
http://127.0.0.1:7861
```

Forge API:

```text
http://127.0.0.1:7860
```

The launcher opens two command windows. Keep both open while using LocalMuse.
The final `.exe` installer is intentionally postponed until the workflow is stable.

## Implemented UI

### Generate

- English/Russian language switch, persisted in browser storage.
- Light/dark theme switch, persisted in browser storage.
- Five built-in prompt presets in `configs/generation_presets.json`.
- LoRA/checkpoint selector.
- Eye-color selector with brown, dark brown, light brown, hazel, green, blue,
  gray, amber, violet, and heterochromia.
- Prompt and negative prompt fields.
- LoRA strength and seed.
- Advanced controls for base model, sampler, steps, CFG, resolution, hires, and
  face-refinement fields.
- Local gallery for generated results.
- `(i)` hover/focus explanations for major settings in English and Russian.
- User presets saved locally to ignored `configs/user_presets.json`.

### Dataset & Training

The UI workflow is:

```text
scan folder -> generate captions -> prepare versioned dataset -> start LoRA training
```

- Scans image count and caption count.
- Starts Florence-2 caption generation as a background job.
- Refuses preparation when any image lacks a same-name `.txt` caption.
- Copies the source into kohya-compatible `repeats_trigger` structure under
  `data/lora_dataset_ui`.
- Training profiles:
  - `Quick test`: 3 epochs, 5 repeats.
  - `Balanced`: 10 epochs, 10 repeats.
  - `Quality`: 13 epochs, 10 repeats.
- Starts SDXL kohya training in the background.

## Models and Paths

Runtime:

```text
E:\ai_work\kohya_ss\.venv\Scripts\python.exe
E:\ai_work\kohya_ss\sd-scripts
```

GPU: NVIDIA GeForce RTX 3080, 10 GB VRAM.

Project-owned caption model:

```text
E:\AI\LocalMuse-AI\models\huggingface
microsoft/Florence-2-large
```

Base model used for the baseline:

```text
E:\AI\LocalMuse-AI\models\base\realvisxlV50_v50Bakedvae.safetensors
```

Installed Forge models/extensions used or planned:

```text
E:\ai_work\webui\models\Stable-diffusion\realvisxlV50_v50Bakedvae.safetensors
E:\ai_work\webui\models\Stable-diffusion\cyberrealisticXL_v100.safetensors
E:\ai_work\webui\models\adetailer\Eyeful_v2-Paired.pt
```

## Pilot Dataset and Training Result

Dataset:

```text
E:\AI\LocalMuse-AI\data\nag_person
```

- 30 PNG images.
- 30 cleaned sidecar captions.
- Trigger token: `nag_person`.
- Captions contain the trigger exactly once.
- No unreadable files or exact SHA-256 duplicates.
- 29 images have one dimension below 512 px.

Baseline:

- RealVisXL 5.0.
- 10 epochs, 3000 steps, 10 repeats.
- LoRA rank 32, alpha 16, FP16, 1024 buckets without upscale.
- Output: `models/lora` locally.
- Result: technically completed, but eye/identity consistency is weaker than the
  older `sid_person` model.

The old known-good run used 39 better images, hand-written Gemini captions, and
3900 steps. It ran for about 6 hours 40 minutes. This comparison is documented in
`Training_Run_nag_person_dataset_v01.md` and is the main reason to wait for a
better `dataset_v02` before retraining.

## Generation Testing Guidance

Quick filter: 5 seeds per prompt.

Reliable comparison: 10-20 seeds across several prompts. Keep base model, seed,
sampler, steps, CFG, resolution, and LoRA weight fixed while comparing checkpoints.
Do not delete failures automatically yet; move them to `rejects` or rate them.

The current useful range for `nag_person_dataset_v01` was roughly LoRA weight
`0.8-1.0`; `0.4` was too weak and `1.2` looked over-strengthened/older.

## Important Known Limitations

- Eyeful is exposed as experimental UI fields, but full Forge API integration is
  not yet verified. Use Forge GUI for the known working ADetailer settings:
  mask blur 4, strength/denoise 0.37, padding 68.
- This Forge build has a hires API issue involving `hr_additional_modules`; GUI
  hires works more reliably than the API path.
- Automatic image ranking/selection is not implemented yet.
- UI job status is basic; detailed training logs and progress are next.
- New photos and generated outputs are ignored by Git. Never commit private images
  or model weights.

## Next Recommended Work

1. Add a real job/progress panel for captions and training.
2. Add checkpoint/result rating and a non-destructive `rejects` workflow.
3. Test Eyeful through Forge GUI/API and connect it safely to the preset.
4. Prepare `dataset_v02` from better photos with detailed reviewed captions.
5. Retrain with the validated profile and compare against `sid_person`.
6. Only after this stabilizes, package the application as an `.exe` installer.

## Repository State

Latest commit:

```text
6013ad2 Add eye color control and prompt presets
```

Latest verification: `python -m pytest -q` -> 13 passed.