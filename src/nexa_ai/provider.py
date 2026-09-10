"""Provider 契约的公开再导出。

契约本体已上移到核心层 nexa_agent.provider；这里保留 nexa_ai 的导入
路径，让现有实现（openai_compatible、fake）与调用方无需改动。
"""

from nexa_agent.provider import ModelProvider

__all__ = ["ModelProvider"]
