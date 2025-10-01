import requests
import json
from typing import List, Dict, Any
import re
from configs import BASE_URL, MODEL, API_KEY
from Prompts import PLAN_PROMPT, STEP_EXECUTION_PROMPT


class AgentWorkflow:
    def __init__(self):
        self.base_url = BASE_URL
        self.model = MODEL
        self.api_key = API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _call_llm(self, messages: List[Dict[str, str]], max_tokens: int = 2000) -> str:
        """调用LLM API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API调用失败: {e}")
            return ""
    
    def generate_plan(self, task: str, max_turns: int = 6) -> str:
        """生成任务计划"""
        print("🔄 正在生成计划...")
        
        # 替换prompt中的模板变量
        plan_prompt = PLAN_PROMPT.replace("{{task}}", task)
        plan_prompt = plan_prompt.replace("{{max_turns - 1}}", str(max_turns - 1))
        
        messages = [
            {"role": "user", "content": plan_prompt}
        ]
        
        plan = self._call_llm(messages, max_tokens=1500)
        print("✅ 计划生成完成")
        return plan
    
    def parse_plan_steps(self, plan: str) -> List[str]:
        """解析计划中的步骤"""
        steps = []
        
        # 寻找##ST开头的步骤
        step_pattern = r'##(ST\d+):(.*?)(?=##ST\d+:|$)'
        matches = re.findall(step_pattern, plan, re.DOTALL)
        
        for step_id, step_content in matches:
            step_text = f"{step_id}: {step_content.strip()}"
            steps.append(step_text)
        
        return steps
    
    def extract_code_and_mcps(self, result: str) -> str:
        """从执行结果中提取Python代码和MCP工具"""
        extracted_content = []
        
        # 提取Python代码块
        python_pattern = r'<python>(.*?)</python>'
        python_matches = re.findall(python_pattern, result, re.DOTALL)
        
        for i, code in enumerate(python_matches, 1):
            code = code.strip()
            if code:
                # 检查是否是MCP工具定义
                if "# MCP Name:" in code:
                    extracted_content.append(f"### MCP Tool {i}:\n```python\n{code}\n```")
                else:
                    extracted_content.append(f"### Python Code {i}:\n```python\n{code}\n```")
        
        return "\n\n".join(extracted_content) if extracted_content else "No previous code or MCP tools available."
    
    def execute_step(self, task: str, plan: str, step: str, step_number: int, context: str = "") -> str:
        """执行单个步骤"""
        print(f"🔄 正在执行步骤 {step_number}: {step}...")
        
        # 构建执行prompt
        execution_prompt = STEP_EXECUTION_PROMPT.replace("{{question}}", task)
        execution_prompt = execution_prompt.replace("{{input_plan}}", plan)
        execution_prompt = execution_prompt.replace("{{max_turns - 1}}", "5")
        execution_prompt = execution_prompt.replace("{{context}}", context)
        
        # 添加当前步骤的具体指令
        step_instruction = f"\n\nNow execute this specific step: {step}\n"
        step_instruction += "Please provide the action/code for this step only, following the format specified in the prompt."
        
        messages = [
            {"role": "user", "content": execution_prompt + step_instruction}
        ]
        
        result = self._call_llm(messages, max_tokens=2000)
        print(f"✅ 步骤 {step_number} 执行完成")
        return result
    
    def run_workflow(self, task: str, max_turns: int = 3) -> Dict[str, Any]:
        """运行完整的工作流程"""
        print("🚀 开始执行Agent工作流程")
        print(f"📝 任务: {task}")
        print("=" * 80)
        
        # 1. 生成计划
        plan = self.generate_plan(task, max_turns)
        
        if not plan:
            return {"error": "计划生成失败"}
        
        print("\n📋 生成的计划:")
        print("-" * 40)
        print(plan)
        print("-" * 40)
        
        # 2. 解析步骤
        steps = self.parse_plan_steps(plan)
        
        if not steps:
            print("⚠️  未能解析出有效步骤，使用原始计划")
            steps = [plan]
        
        print(f"\n🔍 解析出 {len(steps)} 个步骤:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}...")
        
        print("\n" + "=" * 80)
        
        # 3. 执行每个步骤
        results = []
        accumulated_context = ""
        
        for i, step in enumerate(steps, 1):
            print(f"\n📍 执行步骤 {i}/{len(steps)}")
            
            # 执行当前步骤，传入累积的context
            result = self.execute_step(task, plan, step, i, accumulated_context)
            
            # 提取当前步骤的代码和MCP工具，添加到累积context中
            current_context = self.extract_code_and_mcps(result)
            if current_context != "No previous code or MCP tools available.":
                if accumulated_context:
                    accumulated_context += f"\n\n## Step {i} Generated Content:\n{current_context}"
                else:
                    accumulated_context = f"## Step {i} Generated Content:\n{current_context}"
            
            results.append({
                "step_number": i,
                "step_description": step,
                "result": result,
                "extracted_context": current_context
            })
            print(f"📄 步骤 {i} 结果:")
            print("-" * 40)
            print(result + "..." if len(result) > 500 else result)
            print("-" * 40)
            
            # 显示累积的context（仅用于调试）
            if accumulated_context:
                print(f"📚 累积Context长度: {len(accumulated_context)} 字符")
            else:
                print("📚 暂无可用Context")
        
        return {
            "task": task,
            "plan": plan,
            "steps": steps,
            "results": results,
            "total_steps": len(steps)
        }


def main():
    """主函数，用于测试工作流程"""
    workflow = AgentWorkflow()
    
    # 示例任务
    task = """def get_target_for_redirect(target: str, domain: str) -> str:
    '''
    Check if the provided target URL string is within the provided domain.
    If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
    Use https protocol.

    Examples:
        get_target_for_redirect('https://music.example.com', 'example.com') -> 'https://music.example.com'
        get_target_for_redirect('https://example.com/service', 'example.com') -> 'https://example.com/service'
        get_target_for_redirect('https://blog.example.com/posts', 'example.com') -> 'https://blog.example.com/posts'
        get_target_for_redirect('https://another.com', 'example.com') -> 'https://example.com'

    Args:
        target (str): The target URL string.
        domain (str): The domain string, without protocol.

    Returns:
        str: The URL string for redirect.
    '''"""
    
    # 运行工作流程
    result = workflow.run_workflow(task)
    
    # 保存结果
    with open("/Users/shaoshuai/Desktop/code/AILAB/SEB/Reproduce_Alita/workflow_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n🎉 工作流程完成！结果已保存到 workflow_result.json")


if __name__ == "__main__":
    main() 