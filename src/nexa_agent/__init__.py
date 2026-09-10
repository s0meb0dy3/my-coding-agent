"""nexa_agent: 可移植的 agent 大脑 —— 消息、工具、循环、事件、会话。

不依赖任何 CLI/UI，也没有本地配置路径。上层（nexa_coding）通过这里的
公开 API 使用，例如 AgentLoop、AgentHarness、session 子模块。
"""

__all__ = ["session"]
