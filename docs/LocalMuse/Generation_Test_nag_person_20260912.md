# Generation Test: LoRA Weight Comparison

Date: 2026-09-12

## Test Settings

- Base model: `realvisxlV50_v50Bakedvae.safetensors`
- Prompt: `nag_person, realistic portrait photo, looking at the camera, neutral
  expression, natural indoor light, simple background`
- Resolution: 512x912
- Sampler: DPM++ 2M Karras
- Steps: 30
- CFG: 4
- Seed: 241109
- Weights: 0.4, 0.6, 0.8, 1.0, 1.2
- Checkpoints: epochs 5 and 10

## Output

```text
outputs/generation_comparison/weight_grid_contact.jpg
```

The individual files are under `outputs/generation_comparison` in folders named
`epoch_05_weight_XX` and `epoch_10_weight_XX`.

## Initial Conclusion

- Weight 0.4 is too weak and can produce a clearly unrelated face.
- Weights 0.8-1.0 are the most plausible starting range from this test.
- Weight 1.2 reinforces the learned appearance but does not fully solve eye
  identity.
- Epoch 10 is slightly more consistent than epoch 5 in this fixed-seed sample,
  but the eye mismatch remains.

This indicates that weight tuning alone is unlikely to recover the missing eye
identity. The next diagnostic should compare the old known-good `sid_person` LoRA
with the same prompt and settings, then decide whether `dataset_v01` needs a new
training run with better captions, repeats, or source images.