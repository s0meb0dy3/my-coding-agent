"""测试单次执行 prompt 的命令行入口。"""

from __future__ import annotations

import argparse
from io import StringIO

import pytest

from mini_agent.messages import AssistantMessage, TextContent
from mini_ai.events import ProviderErrorEvent, ProviderResponseEndEvent
from mini_ai.fake import FakeProvider
from mini_coding.cli import run_prompt


def _args(tmp_path) -> argparse.Namespace:
    return argparse.Namespace(prompt="读取 README", model="test-model", cwd=tmp_path)


@pytest.mark.asyncio
async def test_run_prompt_prints_final_answer_and_registers_coding_tools(tmp_path):
    """CLI 应输出最终回答，并将四个本地工具交给 Provider。"""
    provider = FakeProvider(
        [
            [
                ProviderResponseEndEvent(
                    message=AssistantMessage(content=[TextContent(text="总结完成")])
                )
            ]
        ]
    )
    stdout, stderr = StringIO(), StringIO()

    exit_code = await run_prompt(_args(tmp_path), provider=provider, stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stdout.getvalue() == "总结完成\n"
    assert stderr.getvalue() == ""
    assert {tool.name for tool in provider.calls[0][3]} == {"read", "write", "edit", "bash"}


@pytest.mark.asyncio
async def test_run_prompt_returns_nonzero_for_provider_error(tmp_path):
    """Provider 失败时 CLI 应在 stderr 报错并返回非零。"""
    provider = FakeProvider([[ProviderErrorEvent(message="连接失败")]])
    stdout, stderr = StringIO(), StringIO()

    exit_code = await run_prompt(_args(tmp_path), provider=provider, stdout=stdout, stderr=stderr)

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert "连接失败" in stderr.getvalue()


@pytest.mark.asyncio
async def test_run_prompt_reports_empty_provider_error(tmp_path):
    """Provider 没有错误详情时，也应给脚本调用者留下可读诊断。"""
    provider = FakeProvider([[ProviderErrorEvent(message="")]])
    stdout, stderr = StringIO(), StringIO()

    exit_code = await run_prompt(_args(tmp_path), provider=provider, stdout=stdout, stderr=stderr)

    assert exit_code == 1
    assert stdout.getvalue() == ""
    assert "Provider 未提供错误详情" in stderr.getvalue()
