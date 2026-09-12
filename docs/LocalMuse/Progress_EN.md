# LocalMuse AI - Progress Log

This file is the working handoff document for future agents and development sessions.
Keep it synchronized with `Progress_RU.md` after every meaningful change.

## Current Status

**Stage:** Early development / research

**Last updated:** 2026-09-12

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

## Not Completed Yet

- Dataset folder structure and dataset versioning.
- Image quality checks, duplicate detection, and dataset analysis.
- Real image captioning or vision-model integration.
- Caption review and editing workflow.
- LoRA training orchestration.
- Checkpoint comparison and identity evaluation.
- Local image generation integration.
- Batch generation and result selection.
- Hardware-aware configuration.
- User interface or application orchestrator.
- Reproducible experiment configuration and result records.

## Current Focus

Define the smallest useful local dataset-preparation workflow before adding model
training or generation integrations. Keep image inspection, caption generation,
training, evaluation, and generation as separate components.

## Verification

- Existing tests should be run with:

  ```text
  pytest
  ```

- Latest run: `python -m pytest -q` passed with 9 tests.
- Florence-2 was verified on the RTX 3080 and generated 30 captions.
- Cleaned captions contain the trigger exactly once, with no empty files or known
  speculative-output patterns.
- All 30 images are readable with no exact duplicates; 29 have one dimension below
  512 px and need to be considered in training settings.
- The current test coverage covers prompt generation, caption cleanup, and dataset QA.

## Stopping Point

The first SDXL LoRA baseline completed for the pilot dataset. The next feature is
fixed-prompt checkpoint comparison and identity evaluation.

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