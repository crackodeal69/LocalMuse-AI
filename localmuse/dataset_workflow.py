from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

TRAINING_PROFILES = {
    "quick_test": {
        "label": "Quick test",
        "description": "Short run for checking that the dataset and setup work.",
        "epochs": 3,
        "repeats": 5,
        "network_dim": 16,
        "network_alpha": 8,
        "learning_rate": 0.0001,
        "text_encoder_lr": 5e-6,
    },
    "balanced": {
        "label": "Balanced",
        "description": "Recommended starting profile for a normal identity LoRA.",
        "epochs": 10,
        "repeats": 10,
        "network_dim": 32,
        "network_alpha": 16,
        "learning_rate": 0.0001,
        "text_encoder_lr": 5e-6,
    },
    "quality": {
        "label": "Quality",
        "description": "Longer run for a cleaner identity result and checkpoint comparison.",
        "epochs": 13,
        "repeats": 10,
        "network_dim": 32,
        "network_alpha": 16,
        "learning_rate": 0.0001,
        "text_encoder_lr": 5e-6,
    },
}


def scan_dataset(directory: str | Path) -> dict[str, Any]:
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise NotADirectoryError(f"Directory not found: {directory}")
    images = sorted(path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS)
    caption_count = sum(path.with_suffix(".txt").is_file() for path in images)
    return {
        "directory": str(directory),
        "image_count": len(images),
        "caption_count": caption_count,
        "missing_caption_count": len(images) - caption_count,
        "images": [path.name for path in images],
    }


def prepare_training_dataset(
    source_directory: str | Path,
    target_root: str | Path,
    trigger_token: str,
    repeats: int,
    version: str,
) -> dict[str, Any]:
    source = Path(source_directory).resolve()
    report = scan_dataset(source)
    if report["image_count"] == 0:
        raise ValueError("Dataset contains no supported images")
    if report["missing_caption_count"]:
        raise ValueError("Every image needs a same-name TXT caption before training")
    if repeats < 1 or repeats > 100:
        raise ValueError("repeats must be between 1 and 100")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", trigger_token):
        raise ValueError("trigger_token may contain only letters, numbers, dot, underscore, and hyphen")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", version):
        raise ValueError("version may contain only letters, numbers, dot, underscore, and hyphen")

    target = Path(target_root).resolve() / version / f"{repeats}_{trigger_token}"
    target.mkdir(parents=True, exist_ok=True)
    for image in source.iterdir():
        if image.is_file() and (image.suffix.lower() in SUPPORTED_EXTENSIONS or image.suffix.lower() == ".txt"):
            shutil.copy2(image, target / image.name)
    return {**report, "target_directory": str(target), "repeats": repeats, "version": version}


def write_training_config(
    path: str | Path,
    model_path: str,
    dataset_root: str,
    output_dir: str,
    logging_dir: str,
    epochs: int,
    profile_id: str = "balanced",
) -> Path:
    profile = TRAINING_PROFILES.get(profile_id)
    if profile is None:
        raise ValueError(f"Unknown training profile: {profile_id}")
    epochs = epochs or int(profile["epochs"])
    config = f'''pretrained_model_name_or_path = "{model_path}"
sdxl = true
train_data_dir = "{dataset_root}"
output_dir = "{output_dir}"
logging_dir = "{logging_dir}"
output_name = "localmuse_training"
resolution = "1024,1024"
enable_bucket = true
bucket_no_upscale = true
bucket_reso_steps = 64
min_bucket_reso = 256
max_bucket_reso = 2048
train_batch_size = 1
max_train_epochs = {int(epochs)}
gradient_accumulation_steps = 1
gradient_checkpointing = true
max_data_loader_n_workers = 0
network_module = "networks.lora"
network_dim = {int(profile["network_dim"])}
network_alpha = {int(profile["network_alpha"])}
learning_rate = {profile["learning_rate"]}
unet_lr = 0.0001
text_encoder_lr = [{profile["text_encoder_lr"]}, {profile["text_encoder_lr"]}]
lr_scheduler = "cosine"
lr_scheduler_num_cycles = 1
lr_warmup_steps = 0.1
optimizer_type = "AdamW8bit"
mixed_precision = "fp16"
save_precision = "fp16"
save_model_as = "safetensors"
cache_latents = true
xformers = true
caption_extension = ".txt"
max_token_length = 75
keep_tokens = 1
save_every_n_epochs = 1
'''
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(config, encoding="utf-8")
    return target