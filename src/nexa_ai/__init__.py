"""nexa_ai: the provider layer — how we talk to models.

Owns network, streaming, and provider-specific protocols (the "ears and mouth").
模型契约（ModelProvider / ProviderEvent）由核心层 nexa_agent 拥有，这里只放
具体实现（OpenAI 兼容 Provider、测试用 fake）。nexa_agent 从不 import 本包。
"""

__all__: list[str] = []
