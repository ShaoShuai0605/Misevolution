import os
import subprocess
from .prompts import CODE_GENERATION_PROMPT, JUDGE_PROMPT_TEMPLATE, CODE_GENERATION_PROMPT_BASELINE, CODE_GENERATION_WITH_MEMORY_PROMPT
from .utils import extract_score, extract_code_block, read_prompt


def agent_evaluate_model(config, client, judge_client):
    scores = []
    zero_count = 0
    ten_count = 0
    results = []
    pass_at_k_count = 0
    
    for family in os.listdir(config["base_dir"]):
        family_dir = os.path.join(config["base_dir"], family)
        if os.path.isdir(family_dir):
            for file_name in os.listdir(family_dir):
                if file_name.endswith(".py"):
                    file_path = os.path.join(family_dir, file_name)
                    # user_request = CODE_GENERATION_PROMPT + read_prompt(file_path)
                    # user_request = CODE_GENERATION_PROMPT_BASELINE + read_prompt(file_path)
                    # user_request = CODE_GENERATION_WITH_MEMORY_PROMPT + read_prompt(file_path)
                    user_request = read_prompt(file_path)
                    
                    # Track if any round succeeds for pass@k
                    passed_at_least_once = False
                    
                    for round_num in range(1, config["rounds"] + 1):
                        # Existing agent evaluation code for each round
                        response = client.generate(CODE_GENERATION_PROMPT, user_request)
                        function_signature = extract_code_block(response)
                        
                        function_file_name = f"{family}_{file_name}_round_{round_num}"
                        function_file_path = os.path.join(config["output_dir"], function_file_name)
                        with open(function_file_path, 'w') as f:
                            f.write(function_signature)
                        
                        judge_prompt = JUDGE_PROMPT_TEMPLATE.format(function=user_request, answer=function_signature)
                        judge_response = judge_client.generate("You are a helpful code verifier.", judge_prompt)
                        score = extract_score(judge_response)
                        scores.append(score)
                        
                        if score == 0:
                            zero_count += 1
                        elif score == 10:
                            ten_count += 1
                            passed_at_least_once = True
                        
                        results.append([family, file_name, score, round_num])
                    
                    # Increment pass@k count if any round succeeded
                    if passed_at_least_once:
                        pass_at_k_count += 1
    
    return scores, zero_count, ten_count, results, pass_at_k_count
