# Training and Generation Workflow

## Manual Training

## Temporary Local Launch

For the current development setup, start both Forge and LocalMuse with one
double-click:

```text
scripts\start_localmuse.bat
```

This opens two command windows. Keep them open while using the application, then
close them when finished. LocalMuse opens at:

```text
http://127.0.0.1:7861
```

The Forge API runs in the background at `http://127.0.0.1:7860`.

This batch launcher is a temporary developer workflow. A proper `.exe` installer
and a single-user application launcher belong to the final packaging stage.

The reproducible training config is committed at:

```text
configs\lora_baseline_dataset_v01.toml
```

To run the same SDXL training again, double-click:

```text
scripts\train_lora_dataset_v01.bat
```

The script uses the existing kohya environment at:

```text
E:\ai_work\kohya_ss\.venv
```

It writes checkpoints to `models\lora` and logs to
`outputs\logs\nag_person_dataset_v01`.

## Quick Checkpoint Comparison

The first run produced checkpoints for epochs 1 through 10. For the first
comparison, use epochs 3, 5, 7, 8, 9, and 10. Do not assume the last checkpoint is
best.

Install one checkpoint into the existing Forge LoRA directory:

```text
scripts\install_lora_for_forge.bat nag_person_dataset_v01-000005.safetensors
```

If no argument is given, epoch 5 is copied by default.

## Forge Generation Test

1. Run `E:\ai_work\run.bat`.
2. Select `realvisxlV50_v50Bakedvae.safetensors` as the base checkpoint.
3. Select the installed `nag_person_dataset_v01-000005` LoRA.
4. Start with LoRA weight `0.8`.
5. Use the same prompt, seed, size, sampler, and steps for every checkpoint.
6. Save the results in separate folders named after the epoch.

Suggested fixed test prompt:

```text
nag_person, realistic portrait photo, looking at the camera, neutral expression,
soft natural window light, simple indoor background, detailed face
```

Suggested first settings for the SDXL base:

```text
Size: 1024x1024
Sampler: DPM++ 2M Karras
Steps: 30
CFG: 5.5-7
Seed: 241109
LoRA weight: 0.6, 0.8, 1.0
```

For a fair comparison, vary only the LoRA checkpoint or weight. Compare identity
similarity, face quality, prompt adherence, and artifacts. The sample images made
during training are useful clues, but the Forge test at a fixed seed is the final
comparison.

## Console Generation

For automated comparison, run:

```text
scripts\start_forge_api.bat
```

After Forge is ready, open another terminal in the project root and run:

```powershell
python scripts\generate_lora_comparison.py
```

By default this generates epochs 3, 5, 7, 8, 9, and 10 with the same seed and
settings. Add `--seeds 241109 241110 241111` to generate several variations per
checkpoint. Results are written to `outputs\generation_comparison\epoch_XX`. The
script uses only the Python standard library and copies each selected LoRA into
Forge automatically.

The comparison script also supports `--weights 0.4 0.6 0.8 1.0 1.2` and the
`--hires` options. The current Forge API build has a hires bug involving a missing
`hr_additional_modules` value; use the Forge GUI for hires until that build is
updated. Base 512x912 API generation works.

## Preset and Advanced Settings Design

Built-in generation presets are stored in:

```text
configs\generation_presets.json
```

The planned user-facing interface has two levels:

- Simple mode: preset, prompt, negative prompt, LoRA weight, and Generate.
- Advanced mode: base model, sampler, steps, CFG, resolution, hires settings,
  face refinement, Eyeful model, mask blur, face denoising strength, and padding.

The initial presets are based on the known working profile rather than arbitrary
online recommendations: 512x912, DPM++ 2M Karras, 30 steps, CFG 4, and LoRA
weight 0.9. The CyberRealistic preset is marked experimental until it is tested
with the same LoRA and fixed seeds.

When a user saves a customized preset, it is written to the local ignored file:

```text
configs\user_presets.json
```

This keeps user preferences separate from versioned built-in presets.

## Dataset and Training UI

The LocalMuse UI now has a `Dataset & training` view at `http://127.0.0.1:7861`.
Its workflow is:

```text
scan photo folder
    -> generate or review captions
    -> prepare a versioned kohya dataset
    -> start LoRA training
```

Training is blocked when an image does not have a same-name TXT caption. Prepared
copies are written under `data/lora_dataset_ui`; the source folder is not changed.
Training runs in the background through the existing kohya SDXL environment.

Training profiles keep the normal workflow small:

- `Quick test`: 3 epochs and 5 repeats for checking a new dataset.
- `Balanced`: 10 epochs and 10 repeats; recommended default.
- `Quality`: 13 epochs and 10 repeats for a longer comparison run.

Rank, alpha, learning rates, precision, buckets, and optimizer are controlled by
the profile. An optional epoch override is available, while the remaining
technical controls stay behind Advanced until real datasets validate them.

For generation evaluation, five seeds are enough for a quick filter. Use 10-20
seeds across several prompts before choosing a checkpoint or preset. Automatic
selection should initially move rejected images to a `rejects` area or attach a
rating, rather than permanently deleting them. A later curation feature can rank
large batches using face quality, identity similarity, prompt adherence, and
duplicate detection.