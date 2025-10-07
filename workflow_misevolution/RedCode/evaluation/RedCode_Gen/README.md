# RedCode-Gen

This directory contains scripts for generating and evaluating malware generation in RedCode-Gen.

Here are the command-line arguments you need to provide:

```
# For normal evaluation
python main.py --model gpt-3.5-turbo --evaluation_type normal

# For agent evaluation
python main.py --model claude-3-opus-20240229 --evaluation_type agent --rounds 3

# To include VirusTotal evaluation
python main.py --model gpt-3.5-turbo --evaluation_type normal --use_virustotal
```

AFlow BasicAuth client usage example:

```
# Use BasicAuth endpoint with the RedCode-Gen dataset root at RedCode/dataset/RedCode-Gen
python -m RedCode_Gen.main \
  --model Qwen2.5-72B-Instruct \
  --evaluation_type normal \
  --base_dir /Users/shaoshuai/Desktop/code/AILAB/SEB/AFlow/RedCode/dataset/RedCode-Gen \
  --output_dir /Users/shaoshuai/Desktop/code/AILAB/SEB/AFlow/RedCode/evaluation/RedCode_Gen/solutions \
  --aflow_base_url https://h.pjlab.org.cn/kapi/workspace.kubebrain.io/ailab-ai4good1/rjob-cef743a168841f3d-8d40ed70322922d2-0.shaoshuai1/19198/v1 \
  --aflow_api_key aa07eff8fee6d7c05902f7d868897ac4 \
  --aflow_secret_key a353737fe891f1125855ec1d79363779 \
  --temperature 0.1 \
  --max_tokens 2048 \
  --top_p 1.0 \
  --families adware,ddos \
  --limit_files 2
```
