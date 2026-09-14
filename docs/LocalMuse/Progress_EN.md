# LocalMuse AI - Progress Log

This file is the working handoff document for future agents and development sessions.
Keep it synchronized with `Progress_RU.md` after every meaningful change.

## Current Status

**Stage:** Working UI prototype and local training pipeline

**Last updated:** 2026-09-14

## Completed

- Created the initial Python package under `localmuse/`.
- Added `ImagePromptGenerator` in `localmuse/image_prompt.py`.
- Added support for JPG, JPEG, PNG, BMP, and WEBP file extensions.
- Added basic image metadata extraction: filename, path, format, dimensions, and orientation.
- Added simple filename-based subject detection for person, face, portrait, and animal keywords.
- Added same-name `.txt` sidecar prompt-file generation for supported images.
- Added directory batch processing for supported image files.
- Added Florence-2 captioning with the `nag_person` trigger token.
- Generated captions for the 30-image `data/nag_person` pilot dataset.
- Added caption cleanup for speculative and identity-related model output.
- Cleaned all 30 pilot captions and kept raw copies outside Git.
- Completed automated and visual review of the pilot dataset; findings are in
  `Dataset_Review_nag_person.md`.
- Added tests for portrait images, landscape images, and unsupported extensions.
- Added tests for same-name TXT files, complex filenames, and directory processing.
- Added the project plan in `docs/LocalMuse/LocalMuse-AI_Project_Plan.md`.
- Added a working LocalMuse UI over Forge API with generation, Dataset & training,
  presets, English/Russian language, and light/dark themes.
- Added eye-color selection, five built-in prompt presets, and localized `(i)`
  setting explanations.
- Kept the RealVisXL base checkpoint, Florence-2 cache, and baseline LoRA
  checkpoints in the project-owned `models/` tree; model files remain ignored by Git.
- Replaced hard-coded Forge and kohya paths in the UI and Forge helper scripts
  with environment-configurable paths and documented fallbacks.

## Not Completed Yet

- Image quality checks, duplicate detection, and dataset analysis.
- Image quality checks, duplicate detection, and dataset analysis.
- Caption review and editing workflow.
- Caption review and editing workflow.
- Detailed job/progress reporting for captioning and training.
- Checkpoint comparison and identity evaluation.
- Local image generation integration.
- Batch generation and result selection.
- Hardware-aware configuration.
- Checkpoint comparison and identity evaluation.
- Reproducible experiment configuration and result records.

## Current Focus

Make the existing UI workflow reliable and observable: add detailed job/progress
reporting, curate generation results, and prepare `dataset_v02` before retraining.

## Verification

- Existing tests should be run with:

  ```text
  pytest
  ```

- Latest run: `python -m pytest -q` passed with 13 tests.
- Florence-2 was verified on the RTX 3080 and generated 30 captions.
- Cleaned captions contain the trigger exactly once, with no empty files or known
  speculative-output patterns.
- All 30 images are readable with no exact duplicates; 29 have one dimension below
  512 px and need to be considered in training settings.
- The current test coverage covers prompt generation, caption cleanup, and dataset QA.
- Batch files for repeating training and installing a selected checkpoint into Forge
  are documented in `Generation_and_Training.md`.
- Browser verification confirmed Forge connection, five presets, Dataset & training,
  language switching, themes, and tooltips.
- Path verification confirmed the project-owned base model and LoRA checkpoints
  are present; external Forge/kohya locations can now be overridden with
  `LOCALMUSE_FORGE_ROOT`, `LOCALMUSE_FORGE_LORA_DIR`, and `LOCALMUSE_KOHYA_ROOT`.

## Stopping Point

The first SDXL LoRA baseline works technically, but `nag_person_dataset_v01` keeps
eyes and identity less reliably than the older `sid_person` model. The UI now
covers generation and profile-based training. Next: job/progress UI, result curation,
and preparation of `dataset_v02`.

## Session Notes

Record each work session using this structure:

```text
Date:
Done:
Not done:
Files changed:
Checks run:
Open questions:
Next step:
```
