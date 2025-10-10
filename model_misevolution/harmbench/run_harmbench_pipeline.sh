#!/bin/bash

# Huggingface related
# export HF_HUB_CACHE=/mnt/shared-storage-user/renqihan/models
# export HF_HUB_OFFLINE=1


export VLLM_USE_MULTIPROCESSING_SPAWN=1
export PYTHON_MULTIPROCESSING_METHOD=spawn

temperature=0.0
method=DirectRequest

behaviors_path=./data/behavior_datasets/harmbench_behaviors_text_all.csv

base_save_dir=./results_harmbench_temp${temperature}

num_tokens=4096

models=(
    # models before self-evolution
    qwen2.5_7b_base
    qwen2.5_7b_coder
    qwen2.5_14b_base
    qwen2.5_14b_coder

    # models after self-evolution
    absolute_zero_7b_base
    absolute_zero_7b_coder
    absolute_zero_14b_base
    absolute_zero_14b_coder
)

for model in "${models[@]}"; do
    echo "Processing model: $model"
    python ./scripts/run_pipeline.py \
        --methods $method \
        --models $model \
        --base_save_dir $base_save_dir \
        --behaviors_path $behaviors_path \
        --step all \
        --mode local \
        --max_new_tokens $num_tokens \
        --temperature $temperature \
        --cls_path cais/HarmBench-Llama-2-13b-cls
done
