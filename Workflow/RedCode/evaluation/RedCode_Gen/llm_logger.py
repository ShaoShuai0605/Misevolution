import json
import datetime
import os
from typing import Dict, Any, List
import threading


class LLMCallLogger:
    """记录LLM调用的query和response"""
    
    def __init__(self, log_file_path: str, enabled: bool = True):
        self.log_file_path = log_file_path
        self.enabled = enabled
        self.calls_log: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(self.log_file_path) if os.path.dirname(self.log_file_path) else ".", exist_ok=True)
    
    def log_call(self, 
                 model: str,
                 query: str, 
                 response: str, 
                 context: Dict[str, Any] = None,
                 error: str = None):
        """记录一次LLM调用"""
        if not self.enabled:
            return
            
        call_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": model,
            "query": query,
            "response": response,
            "context": context or {},
            "error": error,
            "query_length": len(query),
            "response_length": len(response) if response else 0
        }
        
        with self.lock:
            self.calls_log.append(call_info)
            # 实时写入文件，避免程序崩溃时丢失日志
            self._save_to_file()
    
    def _save_to_file(self):
        """保存日志到文件"""
        try:
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.calls_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save LLM call log: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取调用统计信息"""
        if not self.calls_log:
            return {"total_calls": 0}
            
        total_calls = len(self.calls_log)
        total_query_length = sum(call["query_length"] for call in self.calls_log)
        total_response_length = sum(call["response_length"] for call in self.calls_log)
        errors = sum(1 for call in self.calls_log if call.get("error"))
        
        return {
            "total_calls": total_calls,
            "total_query_length": total_query_length,
            "total_response_length": total_response_length,
            "average_query_length": total_query_length / total_calls if total_calls > 0 else 0,
            "average_response_length": total_response_length / total_calls if total_calls > 0 else 0,
            "error_count": errors,
            "success_rate": (total_calls - errors) / total_calls if total_calls > 0 else 0
        }
    
    def print_stats(self):
        """打印调用统计信息"""
        stats = self.get_stats()
        print(f"\n📊 LLM调用统计:")
        print(f"   总调用次数: {stats['total_calls']}")
        print(f"   成功率: {stats.get('success_rate', 0):.2%}")
        print(f"   平均Query长度: {stats.get('average_query_length', 0):.0f} 字符")
        print(f"   平均Response长度: {stats.get('average_response_length', 0):.0f} 字符")
        print(f"   错误次数: {stats.get('error_count', 0)}")
        print(f"   日志文件: {self.log_file_path}")


# 全局日志记录器实例
_global_logger: LLMCallLogger = None


def init_global_logger(log_file_path: str, enabled: bool = True):
    """初始化全局日志记录器"""
    global _global_logger
    _global_logger = LLMCallLogger(log_file_path, enabled)
    return _global_logger


def get_global_logger() -> LLMCallLogger:
    """获取全局日志记录器"""
    return _global_logger


def log_llm_call(model: str, query: str, response: str, context: Dict[str, Any] = None, error: str = None):
    """记录LLM调用的便捷函数"""
    if _global_logger:
        _global_logger.log_call(model, query, response, context, error) 