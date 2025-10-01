import os
import re
import json
import ast
from typing import Dict, List, Tuple, Any
import requests
import sys

API_KEY = "your api key"
MODEL = "your model"
BASE_URL = "your base url"

class CWEvalTaskExtractor:
    def __init__(self, benchmark_path: str = "your benchmark path"):
        self.benchmark_path = benchmark_path
        self.output_dir = "your output dir"
        
    def call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(f"{BASE_URL}chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"调用LLM失败: {e}")
            return ""
    
    def extract_task_content(self, file_path: str) -> Tuple[str, str]:
        """提取任务文件中BEGIN SOLUTION之前的内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找BEGIN SOLUTION之前的内容
        begin_solution_index = content.find('# BEGIN SOLUTION')
        if begin_solution_index == -1:
            return "", ""
        
        # 提取函数定义和文档字符串
        task_content = content[:begin_solution_index].strip()
        
        # 提取函数名
        func_name_match = re.search(r'def (\w+)\(', task_content)
        func_name = func_name_match.group(1) if func_name_match else ""
        
        return task_content, func_name
    
    def extract_pytest_params_functionality(self, file_path: str) -> List[Tuple]:
        """提取测试文件中的pytest_params_functionality内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找pytest_params_functionality的定义
        pattern = r'pytest_params_functionality\s*=\s*\[(.*?)\]'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return []
        
        params_content = match.group(1)
        
        # 解析参数，这里简化处理，提取pytest.param中的参数
        param_matches = re.findall(r'pytest\.param\((.*?),\s*marks=pytest\.mark\.functionality\)', params_content, re.DOTALL)
        
        params = []
        for param_match in param_matches:
            # 简单解析参数，去掉多余的空格和换行
            param_str = param_match.strip().replace('\n', '').replace('        ', ' ')
            # 使用ast.literal_eval安全解析
            try:
                # 将参数字符串包装成元组格式
                if not param_str.startswith('('):
                    param_str = f"({param_str})"
                param_tuple = ast.literal_eval(param_str)
                params.append(param_tuple)
            except:
                # 如果解析失败，手动分割
                parts = [p.strip().strip("'\"") for p in param_str.split(',')]
                params.append(tuple(parts))
        
        return params
    
    def get_all_task_files(self) -> List[str]:
        """获取所有任务文件"""
        task_files = []
        for file in os.listdir(self.benchmark_path):
            if file.endswith('_task.py'):
                task_files.append(os.path.join(self.benchmark_path, file))
        return task_files
    
    def convert_task_to_user_query(self, task_content: str, func_name: str, test_params: List[Tuple]) -> Dict[str, Any]:
        """使用LLM将任务转换为用户查询格式"""
        
        # 构建提示词
        prompt = f"""
Please rewrite the following programming task into a natural language user request in English. Convert the technical task description into something a user would naturally ask for help with.

Original task code:
```python
{task_content}
```

Test case parameters:
{test_params}

Please generate a task_description in the following format:
"I want to handle/process/implement [task description]... For example, when the input is [example input], the output should be [example output]. [Add another example if available]."

Requirements:
1. Use natural, conversational English as if a user is asking for programming help
2. Include 1-2 representative examples from the test cases in the description itself
3. Keep the core functionality of the original task unchanged
4. Make it sound natural and user-friendly
5. Don't generate JSON format, just return the plain task description text

Please only return the task description text, nothing else.
"""
        
        response = self.call_llm(prompt)
        
        # 直接返回LLM的响应作为task_description，如果调用失败则返回默认格式
        if response.strip():
            return {
                "task_description": response.strip(),
                "function_name": func_name,
                "examples": []  # 不再单独存储examples，已包含在task_description中
            }
        else:
            # 如果LLM调用失败，返回默认格式
            example_text = ""
            if test_params:
                example_text = f" For example, when the input is {test_params[0][:-1]}, the output should be {test_params[0][-1]}."
            
            return {
                "task_description": f"I want to implement a function named {func_name}.{example_text}",
                "function_name": func_name,
                "examples": []
            }
    
    def process_all_tasks(self):
        """处理所有任务文件"""
        task_files = self.get_all_task_files()
        
        print(f"找到 {len(task_files)} 个任务文件")
        
        for task_file in task_files:
            try:
                print(f"处理文件: {task_file}")
                
                # 提取任务内容
                task_content, func_name = self.extract_task_content(task_file)
                if not task_content:
                    print(f"跳过 {task_file}: 未找到任务内容")
                    continue
                
                # 查找对应的测试文件
                test_file = task_file.replace('_task.py', '_test.py')
                if not os.path.exists(test_file):
                    print(f"跳过 {task_file}: 未找到对应的测试文件")
                    continue
                
                # 提取测试参数
                test_params = self.extract_pytest_params_functionality(test_file)
                
                # 转换为用户查询格式
                user_query = self.convert_task_to_user_query(task_content, func_name, test_params)
                
                # 保存结果
                output_file = os.path.join(self.output_dir, f"{os.path.basename(task_file).replace('_task.py', '.json')}")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(user_query, f, ensure_ascii=False, indent=2)
                
                print(f"已保存: {output_file}")
                
            except Exception as e:
                print(f"处理 {task_file} 时出错: {e}")
                continue

def main():
    extractor = CWEvalTaskExtractor()
    extractor.process_all_tasks()
    print("所有任务处理完成！")

if __name__ == "__main__":
    main() 