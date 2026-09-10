"""text 模式渲染器：只输出最终答案。

忽略工具过程等细节，只在事件流结束时打印最终助手回答。
这是最"干净"的输出形态，适合管道（pipe）。
"""

from __future__ import annotations

from typing import TextIO

from nexa_agent.events import AgentEndEvent, AgentEvent

# AgentLoop 会把 Provider 错误转成这个前缀开头的助手消息。
ERROR_PREFIX = "错误: "


class FinalTextRenderer:
    """捕获最终答案，finish() 时打印。"""

    def __init__(self, *, stdout: TextIO, stderr: TextIO) -> None:
        """指定输出流：stdout 放答案，stderr 放失败诊断。"""
        self._stdout = stdout
        self._stderr = stderr
        self._final_answer = ""

    def render(self, event: AgentEvent) -> None:
        """只关心 AgentEndEvent，从中提取最终答案。"""

        if isinstance(event, AgentEndEvent):
            # 从后往前找第一条有文字的助手消息，即最终回答。
            for message in reversed(event.messages):
                if message.role == "assistant" and message.text:
                    self._final_answer = message.text
                    break

    def finish(self) -> bool:
        """打印最终答案，返回是否成功。

        成功 = 拿到了有效的最终答案（非空、不是错误开头）。
        失败时把原因写到 stderr，让脚本调用者能看到诊断。
        """

        if not self._final_answer:
            print("错误：模型未返回最终回答", file=self._stderr)
            return False
        if self._final_answer.startswith(ERROR_PREFIX):
            # 保留错误详情（例如 "错误: 连接失败"），但归到 stderr。
            print(self._final_answer, file=self._stderr)
            return False
        print(self._final_answer, file=self._stdout)
        return True


__all__ = ["FinalTextRenderer"]
