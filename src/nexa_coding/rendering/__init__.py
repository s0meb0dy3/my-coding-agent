"""事件渲染器：把 AgentEvent 流变成用户可见的输出。

PrintOutputMode 枚举三种输出形态，create_event_renderer 按模式返回
对应的渲染器。渲染器只观察事件，不改 agent 行为。
"""

from __future__ import annotations

from enum import StrEnum
from typing import TextIO

from nexa_coding.rendering.base import EventRenderer
from nexa_coding.rendering.json import JsonEventRenderer
from nexa_coding.rendering.plain import FinalTextRenderer
from nexa_coding.rendering.transcript import TranscriptRenderer


class PrintOutputMode(StrEnum):
    """CLI 的输出形态。"""

    # 只输出最终答案（默认，适合管道）。
    text = "text"
    # 每个事件一行 JSON。
    json = "json"
    # 工具过程 + 最终答案都显示。
    transcript = "transcript"


def create_event_renderer(
    mode: PrintOutputMode, *, stdout: TextIO, stderr: TextIO
) -> EventRenderer:
    """按模式创建渲染器。

    Args:
        mode: 输出形态（text / json / transcript）。
        stdout: 结果输出流（最终答案 / JSON）。
        stderr: 过程输出流（工具执行细节）。

    Returns:
        实现了 EventRenderer 协议的渲染器实例。
    """

    if mode == PrintOutputMode.text:
        return FinalTextRenderer(stdout=stdout, stderr=stderr)
    if mode == PrintOutputMode.json:
        return JsonEventRenderer(stdout=stdout)
    return TranscriptRenderer(stdout=stdout, stderr=stderr)


__all__ = ["EventRenderer", "PrintOutputMode", "create_event_renderer"]
