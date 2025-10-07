import os
import argparse
from dotenv import load_dotenv

load_dotenv()

def get_config():
    parser = argparse.ArgumentParser(description="RedCode-Gen")
    parser.add_argument("--base_dir", default=os.getenv("BASE_DIR", "./data"), help="Directory containing the prompts")
    parser.add_argument("--output_dir", default=os.getenv("OUTPUT_DIR", "./solutions"), help="Directory to store solutions")
    parser.add_argument("--model", default=os.getenv("MODEL", "gpt-3.5-turbo"), help="Model to evaluate")
    parser.add_argument("--judge_model", default=os.getenv("JUDGE_MODEL", "gpt-4"), help="Model to use for judging")
    parser.add_argument("--evaluation_type", choices=["normal", "agent", "aflow_agent"], default="normal", help="Type of evaluation to perform")
    parser.add_argument("--rounds", type=int, default=5, help="Number of rounds for agent evaluation")
    parser.add_argument("--use_virustotal", action="store_true", help="Use VirusTotal for additional evaluation")
    # AFlow / BasicAuth client parameters
    parser.add_argument("--aflow_base_url", default=os.getenv("AFLOW_BASE_URL", ""), help="AFlow API base url")
    parser.add_argument("--aflow_api_key", default=os.getenv("AFLOW_API_KEY", ""), help="AFlow API key")
    parser.add_argument("--aflow_secret_key", default=os.getenv("AFLOW_SECRET_KEY", ""), help="AFlow secret key")
    parser.add_argument("--aflow_api_path", default=os.getenv("AFLOW_API_PATH", ""), help="Optional API path, e.g. chat/completions")
    parser.add_argument("--temperature", type=float, default=float(os.getenv("AFLOW_TEMPERATURE", 0.1)))
    parser.add_argument("--max_tokens", type=int, default=int(os.getenv("AFLOW_MAX_TOKENS", 2048)))
    parser.add_argument("--top_p", type=float, default=float(os.getenv("AFLOW_TOP_P", 1.0)))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("AFLOW_TIMEOUT", 60)))
    # LLM调用记录功能
    parser.add_argument("--log_llm_calls", action="store_true", help="Log all LLM calls (query + response) to a JSON file")
    parser.add_argument("--llm_log_file", default=os.getenv("LLM_LOG_FILE", "llm_calls_log.json"), help="File path to save LLM call logs")
    # Judge (OpenAI-compatible HTTP with Bearer)
    parser.add_argument("--judge_base_url", default=os.getenv("JUDGE_BASE_URL", ""), help="Judge API base url, e.g. http://host:port/v1/")
    parser.add_argument("--judge_api_key", default=os.getenv("JUDGE_API_KEY", ""), help="Judge API key (Bearer)")
    parser.add_argument("--judge_api_path", default=os.getenv("JUDGE_API_PATH", "chat/completions"), help="Judge API path, default chat/completions")
    parser.add_argument("--judge_timeout", type=int, default=int(os.getenv("JUDGE_TIMEOUT", 60)), help="Judge request timeout seconds")
    # dataset filters
    parser.add_argument("--families", default=os.getenv("FAMILIES", ""), help="Comma separated family names to include only")
    parser.add_argument("--limit_files", type=int, default=int(os.getenv("LIMIT_FILES", 0)), help="Limit number of files per family for quick test (0 = no limit)")
    # extra info for csv naming
    parser.add_argument("--extra_info", default=os.getenv("EXTRA_INFO", ""), help="Extra info suffix for CSV file naming")

    args = parser.parse_args()

    config = {
        "base_dir": args.base_dir,
        "output_dir": args.output_dir,
        "model": args.model,
        "judge_model": args.judge_model,
        "evaluation_type": args.evaluation_type,
        "rounds": args.rounds,
        "use_virustotal": args.use_virustotal,
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "together_api_key": os.getenv("TOGETHER_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "virustotal_api_key": os.getenv("VIRUSTOTAL_API_KEY"),
        # AFlow client configs
        "base_url": args.aflow_base_url,
        "api_key": args.aflow_api_key,
        "secret_key": args.aflow_secret_key,
        "api_path": args.aflow_api_path,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "top_p": args.top_p,
        "timeout": args.timeout,
        # LLM调用记录功能
        "log_llm_calls": args.log_llm_calls,
        "llm_log_file": args.llm_log_file,
        # Judge HTTP client configs
        "judge_base_url": args.judge_base_url,
        "judge_api_key": args.judge_api_key,
        "judge_api_path": args.judge_api_path,
        "judge_timeout": args.judge_timeout,
        # filters
        "families": [f.strip() for f in args.families.split(",") if f.strip()] if args.families else [],
        "limit_files": args.limit_files,
        # extra info
        "extra_info": args.extra_info,
    }

    return config