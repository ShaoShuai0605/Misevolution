AFLOW_API_KEY=YOUR_AFLOW_API_KEY
AFLOW_BASE_URL=YOUR_AFLOW_BASE_URL
JUDGE_BASE_URL=YOUR_JUDGE_BASE_URL
JUDGE_API_KEY=YOUR_JUDGE_API_KEY



python -m RedCode_Gen.main \
  --model Qwen2.5-72B-Instruct \
  --evaluation_type aflow_agent \
  --judge_model gpt-4o \
  --judge_base_url $JUDGE_BASE_URL \
  --judge_api_key $JUDGE_API_KEY \
  --base_dir ../dataset/RedCode-Gen \
  --output_dir ./solutions \
  --aflow_base_url $AFLOW_BASE_URL \
  --aflow_api_key $AFLOW_API_KEY \
  --temperature 0.1 \
  --max_tokens 2048 