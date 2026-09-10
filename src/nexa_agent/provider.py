"""模型 Provider 的统一接口，由可移植的 agent 层拥有。

核心只依赖这个协议，不依赖任何具体 Provider 实现；具体实现在
nexa_ai 里（如 OpenAICompatibleProvider）。这样依赖方向单向：
nexa_ai → nexa_agent。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from nexa_agent.messages import AgentMessage
from nexa_agent.provider_events import ProviderEvent
from nexa_agent.tools import AgentTool


class ModelProvider(Protocol):
    """所有模型后端都要实现的最小接口。"""

    def stream_response(
        self,
        *,
        model: str,
        system: str,
        messages: list[AgentMessage],
        tools: list[AgentTool],
    ) -> AsyncIterator[ProviderEvent]:
        """返回一次模型响应的异步事件流。"""

        ...


__all__ = ["ModelProvider"]
