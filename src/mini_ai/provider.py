"""模型 Provider 的统一接口。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from mini_agent.messages import AgentMessage
from mini_agent.tools import AgentTool
from mini_ai.events import ProviderEvent


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
