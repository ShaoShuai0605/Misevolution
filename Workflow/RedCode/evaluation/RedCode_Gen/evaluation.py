import os
import csv
from .clients import get_client
from .prompts import JUDGE_PROMPT_TEMPLATE, CODE_GENERATION_PROMPT, CODE_GENERATION_PROMPT_BASELINE
from .utils import extract_score, extract_code_block, read_prompt, extract_entry_point_from_signature
from .agent_evaluation import agent_evaluate_model
from .virustotal_evaluation import evaluate_files_on_virustotal
from .clients import OpenAIHTTPClient
from .llm_logger import init_global_logger, get_global_logger

from scripts.async_llm import create_llm_instance
from scripts.operators import CustomCodeGenerate as AFlowCustomCodeGenerate, ScEnsemble as AFlowScEnsemble
import asyncio


def evaluate_model(config):
    # 初始化LLM调用日志记录器
    if config.get("log_llm_calls", False):
        log_file = config.get("llm_log_file", "llm_calls_log.json")
        init_global_logger(log_file, enabled=True)
        print(f"📝 LLM调用日志已启用，将保存到: {log_file}")
    
    client = get_client(config)

    # Build judge client
    if config.get("judge_base_url") and config.get("judge_api_key"):
        judge_client = OpenAIHTTPClient(
            api_key=config["judge_api_key"],
            base_url=config["judge_base_url"],
            model=config.get("judge_model", config["model"]),
            api_path=config.get("judge_api_path", "chat/completions"),
            timeout=int(config.get("judge_timeout", 180)),
            temperature=float(config.get("temperature", 0)),
            max_tokens=int(config.get("max_tokens", 4096))
        )
    elif all(k in config and config[k] for k in ["base_url", "api_key", "secret_key"]):
        judge_cfg = {**config, "model": config["model"]}
        judge_client = get_client(judge_cfg)
    else:
        judge_client = get_client({"model": config["judge_model"], **config})

    os.makedirs(config["output_dir"], exist_ok=True)

    print(f"Starting evaluation with model={config['model']} type={config['evaluation_type']} base_dir={config['base_dir']}")

    if config["evaluation_type"] == "agent":
        scores, zero_count, ten_count, results, pass_at_k_count = agent_evaluate_model(config, client, judge_client)
        pass_at_k_rate = pass_at_k_count / (len(scores) / config["rounds"]) if scores else 0
    elif config["evaluation_type"] == "aflow_agent":
        scores, zero_count, ten_count, results = aflow_agent_evaluate_model(config, judge_client)
        pass_at_k_rate = None
    else:
        scores, zero_count, ten_count, results = normal_evaluate_model(config, client, judge_client)
        pass_at_k_rate = None

    average_score = sum(scores) / len(scores) if scores else 0
    zero_rate = zero_count / len(scores) if scores else 0
    ten_rate = ten_count / len(scores) if scores else 0

    # Save results to CSV with evaluation_type and extra_info suffix
    evaluation_type = config.get("evaluation_type", "normal")
    extra_info = config.get("extra_info", "")
    suffix = f"_{evaluation_type}"
    if extra_info:
        suffix += f"_{extra_info}"
    output_file = f"evaluation_results_{config['model']}{suffix}.csv"
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Family", "File", "Score", "Round"])
        for result in results:
            writer.writerow(result)
        writer.writerow(["Average Score", average_score])
        writer.writerow(["Zero Rate", zero_rate])
        writer.writerow(["Ten Rate", ten_rate])
        if pass_at_k_rate is not None:
            writer.writerow([f"Pass@{config['rounds']}", pass_at_k_rate])

    print(f"Evaluation results saved to {output_file}")
    if pass_at_k_rate is not None:
        print(f"Pass@{config['rounds']} rate: {pass_at_k_rate:.2%}")

    # Save detailed results to a separate CSV
    detailed_output_file = f"detailed_results_{config['model']}{suffix}.csv"
    with open(detailed_output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Family", "File", "Score", "Model", "Evaluation_Type", "Temperature", "Max_Tokens"])
        for result in results:
            writer.writerow([
                result[0],  # Family
                result[1],  # File
                result[2],  # Score
                config['model'],
                evaluation_type,
                config.get('temperature', 0),
                config.get('max_tokens', 2048)
            ])
    print(f"Detailed results saved to {detailed_output_file}")

    # Save summary statistics to a separate CSV
    summary_output_file = f"summary_{config['model']}{suffix}.csv"
    with open(summary_output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Model", config['model']])
        writer.writerow(["Evaluation_Type", evaluation_type])
        writer.writerow(["Total_Files", len(scores)])
        writer.writerow(["Average_Score", f"{average_score:.3f}"])
        writer.writerow(["Zero_Rate", f"{zero_rate:.3f}"])
        writer.writerow(["Ten_Rate", f"{ten_rate:.3f}"])
        writer.writerow(["Temperature", config.get('temperature', 0.1)])
        writer.writerow(["Max_Tokens", config.get('max_tokens', 2048)])
        if pass_at_k_rate is not None:
            writer.writerow([f"Pass@{config['rounds']}", f"{pass_at_k_rate:.3f}"])
    print(f"Summary statistics saved to {summary_output_file}")

    if config.get("use_virustotal", False):
        vt_results, accuracy_count, total_files = evaluate_files_on_virustotal(config)
        vt_output_file = f"virustotal_evaluation_results_{config['model']}{suffix}.csv"
        with open(vt_output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["File Name", "Analysis ID", "Harmless", "Malicious", "Suspicious", "Undetected", "Timeout"])
            for result in vt_results:
                writer.writerow([
                    result['file_name'], 
                    result['analysis_id'], 
                    result['harmless'], 
                    result['malicious'], 
                    result['suspicious'], 
                    result['undetected'], 
                    result['timeout']
                ])
        print(f"VirusTotal evaluation results saved to {vt_output_file}")
        print(f"Final Accuracy: {accuracy_count}/{total_files} ({accuracy_count / total_files:.2%})")
    
    # 显示LLM调用统计信息（如果启用了日志功能）
    if config.get("log_llm_calls", False):
        logger = get_global_logger()
        if logger:
            logger.print_stats()


def iter_families(config):
    base_dir = config["base_dir"]
    selected = set(config.get("families", []) or [])
    for family in os.listdir(base_dir):
        if selected and family not in selected:
            continue
        family_dir = os.path.join(base_dir, family)
        if os.path.isdir(family_dir):
            yield family, family_dir


def normal_evaluate_model(config, client, judge_client):
    scores = []
    zero_count = 0
    ten_count = 0
    results = []
    limit = int(config.get("limit_files", 0) or 0)

    for family, family_dir in iter_families(config):
        processed = 0
        print(f"Processing family: {family}")
        for file_name in os.listdir(family_dir):
            if not file_name.endswith(".py"):
                continue
            if limit and processed >= limit:
                break
            file_path = os.path.join(family_dir, file_name)
            print(f"  -> Generating for file: {file_name}")
            # user_request = CODE_GENERATION_PROMPT + read_prompt(file_path)
            # user_request = CODE_GENERATION_PROMPT_BASELINE + read_prompt(file_path)
            # user_request = CODE_GENERATION_WITH_MEMORY_PROMPT + read_prompt(file_path)
            user_request = read_prompt(file_path)

            try:
                response = client.generate(CODE_GENERATION_WITH_MEMORY_PROMPT, user_request)
                # response = client.generate("you are a helpful code assistant.", user_request)
                print(f"  -> Response: {response}")
            except Exception as e:
                print(f"  !! Generation failed for {file_name}: {e}")
                results.append([family, file_name, -1])
                continue

            function_signature = extract_code_block(response)
            print(f"  -> Function signature: {function_signature}")

            function_file_name = f"{family}_{file_name}"
            function_file_path = os.path.join(config["output_dir"], function_file_name)
            try:
                with open(function_file_path, 'w') as f:
                    f.write(function_signature)
            except Exception as e:
                print(f"  !! Write solution failed for {file_name}: {e}")

        
            judge_prompt = JUDGE_PROMPT_TEMPLATE.format(function=user_request, answer=response)
            try:
                judge_response = judge_client.generate("You are a helpful code verifier.", judge_prompt)
                print(f"  -> Judge response: {judge_response}")
                score = extract_score(judge_response)
            except Exception as e:
                print(f"  !! Judge failed for {file_name}: {e}")
                score = -1

            scores.append(score)

            if score == 0:
                zero_count += 1
            elif score == 10:
                ten_count += 1

            results.append([family, file_name, score])
            print(f"  <- Done {file_name} with score={score}")
            processed += 1

    return scores, zero_count, ten_count, results


def aflow_agent_evaluate_model(config, judge_client):
    scores = []
    zero_count = 0
    ten_count = 0
    results = []
    limit = int(config.get("limit_files", 0) or 0)

    # 构建 AFlow AsyncLLM（使用 openai 兼容 http bearer 或 basic auth 的默认配置文件/或直接从 config 注入）
    # 直接从当前 RedCode 配置构建：
    aflow_llm_cfg = {
        "model": config["model"],
        "temperature": config.get("temperature", 0.1),
        "key": config.get("api_key"),
        "base_url": config.get("base_url"),
        "top_p": config.get("top_p", 1.0),
        "api_type": "custom" if config.get("secret_key") else "openai",
        "secret_key": config.get("secret_key")
    }
    llm = create_llm_instance(aflow_llm_cfg)
    custom_code_generate = AFlowCustomCodeGenerate(llm)
    sc_ensemble = AFlowScEnsemble(llm)

    for family, family_dir in iter_families(config):
        processed = 0
        print(f"Processing family (aflow_agent): {family}")
        for file_name in os.listdir(family_dir):
            if not file_name.endswith(".py"):
                continue
            if limit and processed >= limit:
                break
            file_path = os.path.join(family_dir, file_name)
            print(f"  -> AFLOW generating for file: {file_name}")
            signature_text = read_prompt(file_path)
            user_request = CODE_GENERATION_PROMPT + signature_text
            entry_point = extract_entry_point_from_signature(signature_text)

            async def run_workflow():
                max_retries = 3
                for attempt in range(max_retries):
                    solutions = []
                    for _ in range(3):
                        s = await custom_code_generate(problem=user_request, entry_point=entry_point, instruction="")
                        solutions.append(s['response'])
                    final = await sc_ensemble(solutions=solutions, problem=user_request)
                    # 不执行本地测试，直接用 judge 打分
                    return final['response']
                return ""

            try:
                final_solution = asyncio.run(run_workflow())
            except Exception as e:
                print(f"  !! AFLOW generation failed for {file_name}: {e}")
                results.append([family, file_name, -1])
                continue

            function_file_name = f"{family}_{file_name}"
            function_file_path = os.path.join(config["output_dir"], function_file_name)
            try:
                with open(function_file_path, 'w') as f:
                    f.write(final_solution)
            except Exception as e:
                print(f"  !! Write solution failed for {file_name}: {e}")

            judge_prompt = JUDGE_PROMPT_TEMPLATE.format(function=user_request, answer=final_solution)
            try:
                judge_response = judge_client.generate("You are a helpful code verifier.", judge_prompt)
                score = extract_score(judge_response)
            except Exception as e:
                print(f"  !! Judge failed for {file_name}: {e}")
                score = -1

            scores.append(score)
            if score == 0:
                zero_count += 1
            elif score == 10:
                ten_count += 1

            results.append([family, file_name, score])
            print(f"  <- Done (aflow_agent) {file_name} with score={score}")
            processed += 1

    return scores, zero_count, ten_count, results