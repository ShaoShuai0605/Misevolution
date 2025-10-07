#!/bin/bash

cls_path="$1"
behaviors_path=$2
completions_path=$3
save_path=$4
save_asr_path=$5

echo "cls_path=$cls_path"
echo "behaviors_path=$behaviors_path"
echo "completions_path=$completions_path"
echo "save_path=$save_path"
echo "save_asr_path=$save_asr_path"


python3 -u evaluate_completions.py \
    --cls_path $cls_path \
    --behaviors_path $behaviors_path \
    --completions_path $completions_path \
    --save_path $save_path \
    --save_asr_path $save_asr_path \
    --include_advbench_metric
