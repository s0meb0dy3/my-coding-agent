"""json 模式渲染器：每个事件一行 JSON。

把事件流变成 JSONL 输出——每行一个可解析的 JSON 对象，方便程序消费。
"""

from __future__ import annotations

from typing import TextIO

from nexa_agent.events import AgentEvent


class JsonEventRenderer:
    """把每个事件序列化成一行 JSON 写到 stdout。"""

    def __init__(self, *, stdout: TextIO) -> None:
        """指定输出流（通常 sys.stdout）。"""
        self._stdout = stdout

    def render(self, event: AgentEvent) -> None:
        """把单个事件写成一行 JSON。"""

        # 事件是 Pydantic 模型，自带 JSON 序列化。
        line = event.model_dump_json(exclude_none=True)
        print(line, file=self._stdout)

    def finish(self) -> bool:
        """json 模式没有"失败"概念，事件都输出了就算成功。"""

        return True


__all__ = ["JsonEventRenderer"]
