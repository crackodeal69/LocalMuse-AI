@echo off
"E:\ai_work\kohya_ss\.venv\Scripts\accelerate.exe" launch --num_cpu_threads_per_process=2 sdxl_train_network.py --config_file "%~dp0..\configs\lora_baseline_dataset_v01.toml"