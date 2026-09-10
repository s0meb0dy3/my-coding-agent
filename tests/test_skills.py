"""测试技能（skills）加载、展开、索引，以及 CodingSession.prompt 里的展开。"""

from __future__ import annotations

import pytest

from nexa_agent.messages import AssistantMessage, TextContent
from nexa_agent.session.entries import Entry
from nexa_ai.events import ProviderResponseEndEvent, ProviderResponseStartEvent
from nexa_ai.fake import FakeProvider
from nexa_coding.resources import NexaResourcePaths, ResourceError, parse_markdown_resource
from nexa_coding.session import CodingSession, CodingSessionConfig
from nexa_coding.skills import Skill, build_skill_index, expand_skill_command, load_skills

# ── 辅助函数 ──────────────────────────────────────────────────────────────────


def _write_skill(paths: NexaResourcePaths, rel_path: str, text: str) -> None:
    """在技能目录下写一个文件。"""
    file = paths.skills_dir / rel_path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8")


class InMemorySessionStorage:
    """把条目存在内存列表里，避免测试碰磁盘。"""

    def __init__(self) -> None:
        self._entries: list[Entry] = []

    def append(self, entry: Entry) -> None:
        self._entries.append(entry)

    def read_all(self) -> list[Entry]:
        return list(self._entries)


# ── 测试用例 ──────────────────────────────────────────────────────────────────


# 测试 1：frontmatter 解析（有/无）
def test_parse_markdown_resource_with_and_without_frontmatter():
    """有 frontmatter 时解析出元数据，没有时返回空元数据。"""
    with_frontmatter = """---
name: python-testing
description: 写 pytest 测试
---
正文第一行
正文第二行"""
    metadata, body = parse_markdown_resource(with_frontmatter)
    assert metadata == {"name": "python-testing", "description": "写 pytest 测试"}
    assert body == "正文第一行\n正文第二行"

    # 没有 frontmatter：原样返回。
    no_frontmatter = "直接就是正文"
    metadata2, body2 = parse_markdown_resource(no_frontmatter)
    assert metadata2 == {}
    assert body2 == "直接就是正文"


# 测试 2：skill 加载（两种布局）
def test_load_skills_two_layouts(tmp_path):
    """目录布局和文件布局都能加载。"""
    paths = NexaResourcePaths(root=tmp_path)
    _write_skill(
        paths, "python-testing/SKILL.md", "---\ndescription: 写 pytest 测试\n---\n技能正文 1"
    )
    _write_skill(paths, "bash-helper.md", "---\ndescription: bash 小助手\n---\n技能正文 2")

    skills = load_skills(paths)
    # 按名字排序：bash-helper, python-testing。
    assert [s.name for s in skills] == ["bash-helper", "python-testing"]
    assert skills[0].description == "bash 小助手"
    assert skills[0].content == "技能正文 2"
    assert skills[1].description == "写 pytest 测试"


# 测试 3：重名抛 ResourceError
def test_load_skills_duplicate_name_raises(tmp_path):
    """同名技能（目录布局 + 文件布局）应抛 ResourceError。"""
    paths = NexaResourcePaths(root=tmp_path)
    _write_skill(paths, "dup/SKILL.md", "---\ndescription: 目录版\n---\n正文")
    _write_skill(paths, "dup.md", "---\ndescription: 文件版\n---\n正文")

    with pytest.raises(ResourceError, match="重名"):
        load_skills(paths)


# 测试 4：/skill:name 展开产物正确（带 <skill> 包裹）
def test_expand_skill_command():
    """命中 /skill:name 时返回 <skill> 包裹的展开文本。"""
    skill = Skill(
        name="python-testing",
        path=__file__,
        description="写 pytest 测试",
        content="写一个 pytest 测试文件",
    )
    expanded = expand_skill_command("/skill:python-testing add tests", [skill])
    assert expanded is not None
    assert '<skill name="python-testing">' in expanded
    assert "写一个 pytest 测试文件" in expanded
    assert "<arguments>" in expanded and "add tests" in expanded

    # 未命中返回 None。
    assert expand_skill_command("普通问题", [skill]) is None
    assert expand_skill_command("/skill:nonexistent", [skill]) is None


# 测试 5：build_skill_index 输出
def test_build_skill_index():
    """输出 '- name: description' 列表。"""
    skills = [
        Skill(name="python-testing", path=__file__, description="写 pytest 测试", content="正文"),
        Skill(name="bash-helper", path=__file__, description="bash 小助手", content="正文"),
    ]
    index = build_skill_index(skills)
    assert "可用技能：" in index
    assert "- python-testing: 写 pytest 测试" in index
    assert "- bash-helper: bash 小助手" in index

    # 空列表返回空串。
    assert build_skill_index([]) == ""


# 测试 6：CodingSession.prompt() 里 skill 展开生效（fake provider）
@pytest.mark.asyncio
async def test_prompt_expands_skill_command():
    """prompt('/skill:...') 时，harness 收到的消息应含展开后的技能文本。"""
    skill = Skill(
        name="python-testing",
        path=__file__,
        description="写 pytest 测试",
        content="写一个 pytest 测试文件",
    )
    storage = InMemorySessionStorage()
    provider = FakeProvider(
        [
            [
                ProviderResponseStartEvent(model="test-model"),
                ProviderResponseEndEvent(
                    message=AssistantMessage(content=[TextContent(text="好的，我来写测试")]),
                    finish_reason="stop",
                ),
            ]
        ]
    )
    config = CodingSessionConfig(
        provider=provider,
        model="test-model",
        system="你是助手",
        storage=storage,
        cwd=".",
        skills=[skill],
    )
    session = CodingSession.load(config)

    async for _ in session.prompt("/skill:python-testing add tests"):
        pass

    # FakeProvider 记录下了发给模型的完整消息列表。
    assert provider.calls
    _, _, messages, _ = provider.calls[0]
    user_text = messages[0].text
    assert '<skill name="python-testing">' in user_text
    assert "写一个 pytest 测试文件" in user_text
    assert "add tests" in user_text
