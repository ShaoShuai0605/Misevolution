#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全测试Rollout脚本
读取CWEval/user_queries中的用户查询，使用Agent Workflow进行完整测试
将测试轨迹保存到CWEval/safety_trajs目录
"""

import os
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# 添加当前目录到路径
sys.path.append('./')
from agent_workflow import AgentWorkflow

class SafetyRollout:
    def __init__(self, enable_mcp_matching: bool = True, include_mcp_code: bool = False):
        """初始化安全测试Rollout"""
        self.user_queries_dir = "./user_queries"
        self.safety_trajs_dir = "./safety_trajs"
        
        # 确保输出目录存在
        os.makedirs(self.safety_trajs_dir, exist_ok=True)
        
        # 初始化Agent Workflow
        print("🔄 正在初始化Agent Workflow...")
        self.workflow = AgentWorkflow(
            enable_mcp_matching=enable_mcp_matching,
            include_mcp_code=include_mcp_code
        )
        
        # 显示配置信息
        stats = self.workflow.get_mcp_tools_stats()
        print(f"📊 Agent Workflow配置:")
        print(f"   - MCP匹配: {'启用' if stats.get('enabled', False) else '禁用'}")
        print(f"   - MCP代码包含: {'启用' if stats.get('include_code', False) else '禁用'}")
        print(f"   - 可用MCP工具数: {stats.get('tools_count', 0)}")
        print(f"   - Embedding模型: {'已加载' if stats.get('model_loaded', False) else '未加载'}")
    
    def load_user_queries(self) -> List[tuple]:
        """加载所有用户查询文件"""
        query_files = []
        
        if not os.path.exists(self.user_queries_dir):
            print(f"❌ 用户查询目录不存在: {self.user_queries_dir}")
            return query_files
        
        for filename in os.listdir(self.user_queries_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.user_queries_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        query_data = json.load(f)
                    query_files.append((filename, query_data))
                except Exception as e:
                    print(f"⚠️ 加载查询文件失败 {filename}: {e}")
        
        return sorted(query_files)
    
    def run_single_test(self, filename: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个安全测试"""
        user_query = query_data.get('user_query', '')
        original_task = query_data.get('original_task', '')
        
        if not user_query:
            print(f"⚠️ 用户查询为空: {filename}")
            return None
        
        print(f"📝 用户查询: {user_query[:100]}...")
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 运行Agent Workflow
            workflow_result = self.workflow.run_workflow(user_query, max_turns=5)
            
            # 记录结束时间
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 构建完整的测试轨迹
            trajectory = {
                "test_info": {
                    "filename": filename,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time_seconds": round(execution_time, 2)
                },
                "input": {
                    "user_query": user_query,
                    "original_task": original_task
                },
                "workflow_execution": workflow_result,
                "success": "error" not in workflow_result,
                "total_steps": workflow_result.get("total_steps", 0),
                "agent_config": self.workflow.get_mcp_tools_stats()
            }
            
            return trajectory
            
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            
            # 返回错误轨迹
            error_trajectory = {
                "test_info": {
                    "filename": filename,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time_seconds": 0
                },
                "input": {
                    "user_query": user_query,
                    "original_task": original_task
                },
                "workflow_execution": {"error": str(e)},
                "success": False,
                "total_steps": 0,
                "agent_config": self.workflow.get_mcp_tools_stats()
            }
            
            return error_trajectory
    
    def save_trajectory(self, filename: str, trajectory: Dict[str, Any]):
        """保存测试轨迹"""
        # 生成轨迹文件名（保持与原文件名的对应关系）
        base_name = filename.replace('.json', '')
        traj_filename = f"{base_name}_safety_trajectory.json"
        output_path = os.path.join(self.safety_trajs_dir, traj_filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(trajectory, f, ensure_ascii=False, indent=2)
            print(f"✅ 轨迹保存成功: {traj_filename}")
        except Exception as e:
            print(f"❌ 轨迹保存失败 {traj_filename}: {e}")
    
    def run_all_tests(self, limit: int = None):
        """运行所有安全测试"""
        print("🚀 开始安全测试Rollout")
        print("=" * 80)
        
        # 加载所有用户查询
        query_files = self.load_user_queries()
        
        if not query_files:
            print("❌ 未找到用户查询文件")
            return
        
        # 应用限制
        if limit and limit > 0:
            query_files = query_files[:limit]
            print(f"📊 限制测试数量: {limit}")
        
        print(f"📊 找到 {len(query_files)} 个用户查询文件")
        
        success_count = 0
        failed_count = 0
        total_execution_time = 0
        
        for i, (filename, query_data) in enumerate(query_files, 1):
            print(f"\n📍 测试 {i}/{len(query_files)}: {filename}")
            print("-" * 60)
            
            # 运行单个测试
            trajectory = self.run_single_test(filename, query_data)
            
            if trajectory:
                # 保存轨迹
                self.save_trajectory(filename, trajectory)
                
                # 统计信息
                if trajectory.get('success', False):
                    success_count += 1
                    print(f"✅ 测试成功")
                else:
                    failed_count += 1
                    print(f"❌ 测试失败")
                
                execution_time = trajectory.get('test_info', {}).get('execution_time_seconds', 0)
                total_execution_time += execution_time
                print(f"⏱️ 执行时间: {execution_time:.2f}秒")
                
                # 显示简要结果
                workflow_result = trajectory.get('workflow_execution', {})
                if 'total_steps' in workflow_result:
                    print(f"📋 执行步骤数: {workflow_result['total_steps']}")
                
            else:
                failed_count += 1
                print(f"❌ 测试完全失败")
            
            print("-" * 60)
        
        # 输出总结
        print("\n" + "=" * 80)
        print(f"🎉 安全测试Rollout完成!")
        print(f"✅ 成功: {success_count} 个")
        print(f"❌ 失败: {failed_count} 个")
        print(f"📈 成功率: {(success_count / len(query_files) * 100):.1f}%")
        print(f"⏱️ 总执行时间: {total_execution_time:.2f}秒")
        print(f"⏱️ 平均执行时间: {(total_execution_time / len(query_files)):.2f}秒")
        print(f"📁 轨迹保存目录: {self.safety_trajs_dir}")
    
    def run_sample_tests(self, sample_count: int = 3):
        """运行样本测试（用于快速验证）"""
        print(f"🧪 运行 {sample_count} 个样本测试")
        print("=" * 80)
        
        query_files = self.load_user_queries()
        
        if not query_files:
            print("❌ 未找到用户查询文件")
            return
        
        # 选择前几个文件作为样本
        sample_files = query_files[:sample_count]
        
        for i, (filename, query_data) in enumerate(sample_files, 1):
            print(f"\n🧪 样本测试 {i}/{len(sample_files)}: {filename}")
            print("-" * 60)
            
            user_query = query_data.get('user_query', '')
            print(f"📝 用户查询: {user_query}")
            
            # 只运行计划生成，不执行完整流程
            try:
                plan = self.workflow.generate_plan(user_query, max_turns=4)
                if plan:
                    print(f"✅ 计划生成成功")
                    print(f"📋 计划长度: {len(plan)} 字符")
                    print(f"📄 计划预览: {plan[:200]}...")
                else:
                    print(f"❌ 计划生成失败")
            except Exception as e:
                print(f"❌ 样本测试失败: {e}")
            
            print("-" * 60)
    
    def analyze_existing_trajectories(self):
        """分析已有的轨迹文件"""
        print("📊 分析已有的安全测试轨迹")
        print("=" * 80)
        
        if not os.path.exists(self.safety_trajs_dir):
            print("❌ 轨迹目录不存在")
            return
        
        traj_files = [f for f in os.listdir(self.safety_trajs_dir) if f.endswith('.json')]
        
        if not traj_files:
            print("❌ 未找到轨迹文件")
            return
        
        print(f"📊 找到 {len(traj_files)} 个轨迹文件")
        
        success_count = 0
        failed_count = 0
        total_steps = 0
        total_time = 0
        
        for filename in traj_files:
            filepath = os.path.join(self.safety_trajs_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    trajectory = json.load(f)
                
                if trajectory.get('success', False):
                    success_count += 1
                else:
                    failed_count += 1
                
                total_steps += trajectory.get('total_steps', 0)
                total_time += trajectory.get('test_info', {}).get('execution_time_seconds', 0)
                
            except Exception as e:
                print(f"⚠️ 读取轨迹文件失败 {filename}: {e}")
        
        print(f"\n📈 轨迹分析结果:")
        print(f"✅ 成功测试: {success_count}")
        print(f"❌ 失败测试: {failed_count}")
        print(f"📈 成功率: {(success_count / len(traj_files) * 100):.1f}%")
        print(f"📋 平均步骤数: {(total_steps / len(traj_files)):.1f}")
        print(f"⏱️ 平均执行时间: {(total_time / len(traj_files)):.2f}秒")

def main():
    print("🤖 CWEval 安全测试Rollout系统")
    print("1. 运行样本测试（3个）")
    print("2. 运行限制测试（指定数量）")
    print("3. 运行全部测试")
    print("4. 分析已有轨迹")
    
    choice = input("\n请选择操作 (1/2/3/4): ").strip()
    
    # 询问配置
    enable_mcp = input("是否启用MCP工具匹配? (y/N): ").strip().lower() == 'y'
    include_code = False
    if enable_mcp:
        include_code = input("是否在prompt中包含MCP工具代码? (y/N): ").strip().lower() == 'y'
    
    # 创建Rollout实例
    rollout = SafetyRollout(
        enable_mcp_matching=enable_mcp,
        include_mcp_code=include_code
    )
    
    if choice == "1":
        rollout.run_sample_tests(3)
    elif choice == "2":
        try:
            limit = int(input("请输入测试数量限制: ").strip())
            rollout.run_all_tests(limit=limit)
        except ValueError:
            print("❌ 无效的数量")
    elif choice == "3":
        confirm = input("确认要运行所有测试吗？这可能需要很长时间。(y/N): ").strip().lower()
        if confirm == 'y':
            rollout.run_all_tests()
        else:
            print("操作已取消")
    elif choice == "4":
        rollout.analyze_existing_trajectories()
    else:
        print("无效选择")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用户中断")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
