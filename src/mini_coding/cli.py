"""单次执行 prompt 的命令行入口。"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import TextIO

from mini_agent.events import AgentEndEvent, ToolExecutionEndEvent, ToolExecutionStartEvent
from mini_agent.harness import AgentHarness, AgentHarnessConfig
from mini_ai.openai_compatible import OpenAICompatibleProvider
from mini_ai.provider import ModelProvider
from mini_coding.tools import create_coding_tools

DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"
SYSTEM_PROMPT = "你是一个谨慎的 coding agent。需要时使用工具，并简洁地报告结果。"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析这个一次性命令所需的最小参数。"""
    parser = argparse.ArgumentParser(description="运行一次 coding agent prompt")
    parser.add_argument("-p", "--print", dest="prompt", required=True, help="要执行的 prompt")
    parser.add_argument("--model", default=os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL))
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="工具可访问的项目目录")
    return parser.parse_args(argv)


def create_provider() -> OpenAICompatibleProvider:
    """从环境变量创建 OpenAI 兼容 Provider。"""
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置 DEEPSEEK_API_KEY（或 OPENAI_API_KEY）")

    return OpenAICompatibleProvider(
        name="deepseek",
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL)),
    )


async def run_prompt(
    args: argparse.Namespace,
    *,
    provider: ModelProvider | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    """运行一条 prompt，并把最终回答和运行诊断分流输出。"""
    try:
        cwd = args.cwd.resolve()
        if not cwd.is_dir():
            print(f"错误：--cwd 不是目录：{cwd}", file=stderr)
            return 2

        harness = AgentHarness(
            AgentHarnessConfig(
                provider=provider or create_provider(),
                model=args.model,
                system=SYSTEM_PROMPT,
                tools=create_coding_tools(cwd),
            )
        )
        failed = False
        final_answer = ""

        async for event in harness.prompt(args.prompt):
            if isinstance(event, ToolExecutionStartEvent):
                print(f"工具开始：{event.tool_name}", file=stderr)
            elif isinstance(event, ToolExecutionEndEvent):
                prefix = "工具失败" if event.is_error else "工具结束"
                print(f"{prefix}：{event.tool_name}", file=stderr)
                failed |= event.is_error
            elif isinstance(event, AgentEndEvent):
                for message in reversed(event.messages):
                    if message.role == "assistant" and message.text:
                        final_answer = message.text
                        break

        # AgentLoop 会把 Provider 错误转换成此形式的最终助手消息。
        if final_answer.startswith("错误: "):
            print(final_answer, file=stderr)
            return 1
        if not final_answer:
            print("错误：模型未返回最终回答", file=stderr)
            return 1
        print(final_answer, file=stdout)
        return 1 if failed else 0
    except (OSError, ValueError) as error:
        print(f"错误：{error}", file=stderr)
        return 2


def main(argv: list[str] | None = None) -> None:
    """控制台脚本入口。"""
    args = parse_args(argv)
    raise SystemExit(asyncio.run(run_prompt(args)))


__all__ = ["create_provider", "main", "parse_args", "run_prompt"]
