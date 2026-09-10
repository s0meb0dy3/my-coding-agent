"""渲染器协议：所有事件渲染器的统一接口。

渲染器只负责"事件怎么显示"，不决定 agent 跑什么——绝不调 harness 或
session 的方法。render() 观察事件，finish() 在流结束后返回是否成功，
供 CLI 决定退出码。
"""

from __future__ import annotations

from typing import Protocol

from nexa_agent.events import AgentEvent


class EventRenderer(Protocol):
    """把 AgentEvent 流渲染成用户可见的输出。"""

    def render(self, event: AgentEvent) -> None:
        """处理一个事件。"""
        ...

    def finish(self) -> bool:
        """事件流结束后调用，返回是否成功（供退出码使用）。"""
        ...


__all__ = ["EventRenderer"]
