# Training Run: `nag_person_dataset_v01`

Date: 2026-09-12

## Configuration

- Base model: RealVisXL 5.0 checkpoint
- Base model path: `models/base/realvisxlV50_v50Bakedvae.safetensors`
- Dataset: 30 images, 10 repeats, 300 training images per epoch
- Trigger token: `nag_person`
- Resolution: 1024 buckets with no upscale
- LoRA rank: 32
- LoRA alpha: 16
- Batch size: 1
- Epochs: 10
- Total steps: 3000
- Mixed precision: FP16

## Result

- Training completed successfully through epoch 10.
- Final average loss reported by kohya: approximately `0.107`.
- Checkpoints were saved after epochs 1 through 9 and as the final model.
- Sample images were generated for comparison at every epoch.

Output directory:

```text
E:\AI\LocalMuse-AI\models\lora
```

## Initial Visual Evaluation

The run is technically valid, but the samples do not yet establish that the
identity is reliable. Several samples show different-looking faces or strong
style changes. The final epoch must not be selected solely because it has the
lowest or latest loss.

The next evaluation should compare epochs 3, 5, 7, 8, 9, and 10 using the same
fixed prompts, seed policy, resolution, and LoRA weight. Record identity
similarity, face quality, prompt adherence, and artifacts for each checkpoint.

## Important Training Note

The source images are mostly around 405x720 pixels. The current run uses buckets
without upscaling, so most training buckets are approximately 384x704. A later
experiment can compare this baseline with a carefully prepared higher-resolution
copy, but that should be a separate dataset version and not overwrite `dataset_v01`.