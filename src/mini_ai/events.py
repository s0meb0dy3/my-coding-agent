"""模型 Provider 输出的最小、统一事件。"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from mini_agent.messages import AssistantMessage, ToolCall, WireModel


class ProviderResponseStartEvent(WireModel):
    """模型开始生成一次响应。"""

    type: Literal["response_start"] = "response_start"
    model: str


class ProviderTextDeltaEvent(WireModel):
    """模型流式输出的一小段文本。"""

    type: Literal["text_delta"] = "text_delta"
    delta: str


class ProviderToolCallEvent(WireModel):
    """模型请求调用工具；Provider 不在这里执行工具。"""

    type: Literal["tool_call"] = "tool_call"
    tool_call: ToolCall


class ProviderResponseEndEvent(WireModel):
    """模型响应结束，并携带累积后的助手消息。"""

    type: Literal["response_end"] = "response_end"
    message: AssistantMessage
    finish_reason: str | None = None


class ProviderErrorEvent(WireModel):
    """Provider 或模型 API 返回错误。"""

    type: Literal["error"] = "error"
    message: str


# 根据 type 字段，Pydantic 可以把字典解析成对应的事件类。
type ProviderEvent = Annotated[
    ProviderResponseStartEvent
    | ProviderTextDeltaEvent
    | ProviderToolCallEvent
    | ProviderResponseEndEvent
    | ProviderErrorEvent,
    Field(discriminator="type"),
]


__all__ = [
    "ProviderErrorEvent",
    "ProviderEvent",
    "ProviderResponseEndEvent",
    "ProviderResponseStartEvent",
    "ProviderTextDeltaEvent",
    "ProviderToolCallEvent",
]
