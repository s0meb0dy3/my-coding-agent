"""单次执行 prompt 的命令行入口。"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import TextIO

from nexa_agent.harness import AgentHarness, AgentHarnessConfig
from nexa_ai.openai_compatible import OpenAICompatibleProvider
from nexa_ai.provider import ModelProvider
from nexa_coding.rendering import PrintOutputMode, create_event_renderer
from nexa_coding.tools import create_coding_tools
from nexa_coding.tui import NexaTuiApp

DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"
SYSTEM_PROMPT = "你是一个谨慎的 coding agent。需要时使用工具，并简洁地报告结果。"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析这个一次性命令所需的最小参数。"""
    parser = argparse.ArgumentParser(description="运行一次 coding agent prompt")
    parser.add_argument(
        "-p",
        "--print",
        dest="prompt",
        help="要执行的 prompt（print 模式必填；TUI 模式不需要）",
    )
    parser.add_argument("--model", default=os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL))
    parser.add_argument(
        "--output",
        type=PrintOutputMode,
        default=PrintOutputMode.text,
        choices=list(PrintOutputMode),
        help="输出形态：text / json / transcript（默认 text）",
    )
    parser.add_argument("--tui", action="store_true", help="打开交互式 TUI 界面")
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="工具可访问的项目目录")
    args = parser.parse_args(argv)

    # print 模式（默认）必须有 -p；TUI 模式不需要。
    if not args.tui and not args.prompt:
        parser.error("print 模式需要 -p/--print 参数（或用 --tui 打开交互界面）")

    return args


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

        # 渲染器把事件流变成输出；只观察，不改 agent 行为。
        renderer = create_event_renderer(args.output, stdout=stdout, stderr=stderr)

        async for event in harness.prompt(args.prompt):
            renderer.render(event)

        # finish() 返回是否成功，直接作为 CLI 退出码。
        return 0 if renderer.finish() else 1
    except (OSError, ValueError) as error:
        print(f"错误：{error}", file=stderr)
        return 2


def main(argv: list[str] | None = None) -> None:
    """控制台脚本入口。"""
    args = parse_args(argv)
    if args.tui:
        try:
            # Textual 自管事件循环，直接调用 App.run()，不要包 asyncio.run()。
            NexaTuiApp(create_provider(), model=args.model).run()
        except ValueError as error:
            # 例如没配 API key：给出友好提示而不是堆栈。
            print(f"错误：{error}", file=sys.stderr)
            raise SystemExit(2) from None
        return
    raise SystemExit(asyncio.run(run_prompt(args)))


__all__ = ["create_provider", "main", "parse_args", "run_prompt"]
