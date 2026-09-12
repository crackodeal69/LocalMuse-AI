# Training and Generation Workflow

## Manual Training

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