# Dataset Review: `nag_person`

Date: 2026-09-12

## Automated Checks

- 30 supported PNG images found.
- 30 sidecar captions found.
- Every caption contains `nag_person` exactly once.
- No unreadable images detected.
- No exact duplicate files detected by SHA-256.
- 29 images have a dimension below 512 pixels, usually a width of about 405
  pixels. This is a resolution warning, not an automatic rejection.

## Visual Review

The subject is clearly visible in all 30 contact-sheet frames. The set contains
useful variation in:

- indoor and outdoor backgrounds;
- coats, shirts, jackets, dresses, and dark clothing;
- car, home, street, and park settings;
- direct portraits, selfies, seated frames, and hand gestures;
- lighting and facial expressions.

## Review Risks

- Frames 10, 13, 16, and 19 are similar dark car-seat shots. Keep one or two
  representative examples if the first training run overfits this setting.
- Frames 11 and 26 also share a car setting, but have different lighting and
  clothing.
- Several frames are close to the same portrait composition. This is acceptable
  for an identity LoRA, but the dataset should not grow with many more near-
  identical shots.
- The model captions are cleaned drafts. Clothing colors, hair color, and small
  background details still require human confirmation.

## Recommendation Before Training

Use all 30 images for the first short pilot run, but keep the following record:

```text
dataset_v01
images: 30
trigger: nag_person
caption_model: microsoft/Florence-2-large
caption_review: automated cleanup + contact-sheet review
resolution_warning: 29 images below 512 px on one dimension
```

Do not upscale the source files yet. First compare the baseline training result;
then test a prepared copy with a consistent training resolution if the source
resolution becomes a measurable limitation.