import os
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List


from agent_workflow import AgentWorkflow

class CWEvalEvaluator:
    def __init__(self):
        self.tasks_dir = "your tasks dir"
        self.trajs_dir = "your trajs dir"
        self.workflow = AgentWorkflow()
        
        # 确保trajs目录存在
        os.makedirs(self.trajs_dir, exist_ok=True)
        
    def load_task(self, task_file: str) -> Dict[str, Any]:
        """加载单个任务文件"""
        with open(task_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_task_files(self) -> List[str]:
        """获取所有任务文件"""
        task_files = []
        for file in os.listdir(self.tasks_dir):
            if file.endswith('.json'):
                task_files.append(os.path.join(self.tasks_dir, file))
        return sorted(task_files)
    
    def save_trajectory(self, task_name: str, task_data: Dict[str, Any], workflow_result: Dict[str, Any]):
        """保存执行轨迹"""
        trajectory = {
            "task_name": task_name,
            "timestamp": datetime.now().isoformat(),
            "original_task": task_data,
            "workflow_execution": workflow_result,
            "success": "error" not in workflow_result,
            "total_steps": workflow_result.get("total_steps", 0)
        }
        
        # 保存到trajs目录
        traj_file = os.path.join(self.trajs_dir, f"{task_name}_trajectory.json")
        with open(traj_file, 'w', encoding='utf-8') as f:
            json.dump(trajectory, f, ensure_ascii=False, indent=2)
        
        print(f"📁 轨迹已保存: {traj_file}")
        return traj_file
    
    def evaluate_single_task(self, task_file: str) -> Dict[str, Any]:
        """评估单个任务"""
        task_name = os.path.basename(task_file).replace('.json', '')
        
        print(f"\n{'='*80}")
        print(f"🎯 开始评估任务: {task_name}")
        print(f"{'='*80}")
        
        try:
            # 1. 加载任务
            task_data = self.load_task(task_file)
            task_description = task_data.get("task_description", "")
            function_name = task_data.get("function_name", "")
            
            if not task_description:
                print(f"❌ 任务 {task_name}: 缺少任务描述")
                return {"error": "缺少任务描述"}
            
            print(f"📝 任务描述: {task_description}")
            print(f"🔧 函数名: {function_name}")
            
            # 2. 运行workflow
            print(f"\n🚀 开始执行Agent工作流程...")
            start_time = time.time()
            
            workflow_result = self.workflow.run_workflow(task_description, max_turns=6)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"\n⏱️  执行时间: {execution_time:.2f} 秒")
            
            # 3. 保存轨迹
            traj_file = self.save_trajectory(task_name, task_data, workflow_result)
            
            # 4. 返回评估结果
            result = {
                "task_name": task_name,
                "success": "error" not in workflow_result,
                "execution_time": execution_time,
                "total_steps": workflow_result.get("total_steps", 0),
                "trajectory_file": traj_file,
                "workflow_result": workflow_result
            }
            
            if result["success"]:
                print(f"✅ 任务 {task_name} 执行成功!")
            else:
                print(f"❌ 任务 {task_name} 执行失败: {workflow_result.get('error', '未知错误')}")
            
            return result
            
        except Exception as e:
            print(f"❌ 任务 {task_name} 评估失败: {e}")
            return {
                "task_name": task_name,
                "success": False,
                "error": str(e),
                "execution_time": 0,
                "total_steps": 0
            }
    
    def evaluate_all_tasks(self, max_tasks: int = None) -> Dict[str, Any]:
        """评估所有任务"""
        task_files = self.get_all_task_files()
        
        if max_tasks:
            task_files = task_files[:max_tasks]
        
        print(f"🎯 开始评估 {len(task_files)} 个任务")
        print(f"📁 轨迹保存目录: {self.trajs_dir}")
        print("="*80)
        
        results = []
        successful_tasks = 0
        failed_tasks = 0
        total_execution_time = 0
        
        for i, task_file in enumerate(task_files, 1):
            print(f"\n📊 进度: {i}/{len(task_files)}")
            
            try:
                result = self.evaluate_single_task(task_file)
                results.append(result)
                
                if result.get("success", False):
                    successful_tasks += 1
                else:
                    failed_tasks += 1
                
                total_execution_time += result.get("execution_time", 0)
                
                # 在任务之间添加短暂延迟，避免API频率限制
                if i < len(task_files):
                    print("⏸️  等待2秒...")
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  用户中断评估，已完成 {i-1}/{len(task_files)} 个任务")
                break
            except Exception as e:
                print(f"❌ 评估任务时发生错误: {e}")
                failed_tasks += 1
                results.append({
                    "task_name": os.path.basename(task_file).replace('.json', ''),
                    "success": False,
                    "error": str(e),
                    "execution_time": 0,
                    "total_steps": 0
                })
        
        # 生成总结报告
        summary = {
            "total_tasks": len(task_files),
            "evaluated_tasks": len(results),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / len(results) * 100 if results else 0,
            "total_execution_time": total_execution_time,
            "average_execution_time": total_execution_time / len(results) if results else 0,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        # 保存总结报告
        summary_file = os.path.join(self.trajs_dir, "evaluation_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 打印总结
        print(f"\n{'='*80}")
        print("📊 评估总结")
        print(f"{'='*80}")
        print(f"📈 总任务数: {summary['total_tasks']}")
        print(f"✅ 成功任务: {successful_tasks}")
        print(f"❌ 失败任务: {failed_tasks}")
        print(f"📊 成功率: {summary['success_rate']:.1f}%")
        print(f"⏱️  总执行时间: {total_execution_time:.2f} 秒")
        print(f"⏱️  平均执行时间: {summary['average_execution_time']:.2f} 秒")
        print(f"📁 总结报告: {summary_file}")
        print(f"📁 轨迹目录: {self.trajs_dir}")
        
        return summary

def main():
    """主函数"""
    evaluator = CWEvalEvaluator()
    
    print("🎯 CWEval 任务评估器")
    print("="*80)
    
    # 评估所有任务
    print("🚀 开始评估所有25个任务")
    print("如需限制评估数量，请修改 max_tasks 参数")
    
    try:
        summary = evaluator.evaluate_all_tasks(max_tasks=None)
        
        print(f"\n🎉 评估完成!")
        print(f"成功率: {summary['success_rate']:.1f}%")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  评估被用户中断")
    except Exception as e:
        print(f"❌ 评估过程中发生错误: {e}")

if __name__ == "__main__":
    main() 