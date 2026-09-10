"""NEXA 的资源路径与 markdown 资源解析。

资源（resource）是指 agent 加载的本地知识文件：技能（skills）、提示模板
（prompt templates）等。本模块负责两件事：
- 定义这些资源从哪里找（路径）
- 解析一个 markdown 资源的 frontmatter（--- 包裹的 key: value 头部）
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ResourceError(ValueError):
    """资源加载或解析出错时抛出。"""


@dataclass(frozen=True)
class NexaResourcePaths:
    """NEXA 资源目录的约定路径。

    Attributes:
        root: 资源根目录，默认 ~/.nexa。
        skills_dir: 技能目录，默认 <root>/skills。
        prompts_dir: 提示模板目录，默认 <root>/prompts。
    """

    root: Path = Path.home() / ".nexa"

    @property
    def skills_dir(self) -> Path:
        """技能存放目录。"""
        return self.root / "skills"

    @property
    def prompts_dir(self) -> Path:
        """提示模板存放目录。"""
        return self.root / "prompts"


def parse_markdown_resource(text: str) -> tuple[dict[str, str], str]:
    """解析一个 markdown 资源的 frontmatter，返回 (元数据, 正文)。

    frontmatter 是文件最开头的 `---` 包裹的 `key: value` 行：

        ---
        name: python-testing
        description: 写 pytest 测试
        ---
        正文从这里开始

    没有 frontmatter 时返回 ({}, 原文)。

    Args:
        text: 资源文件的完整文本。

    Returns:
        (metadata, body)：元数据字典和正文 markdown。
    """

    # 必须从文件开头就是 ---，否则不算 frontmatter。
    if not text.startswith("---"):
        return {}, text

    # 找到第二行 --- 的位置。
    lines = text.splitlines()
    end_index: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    # 只有开头一个 ---，没有闭合，视为无 frontmatter。
    if end_index is None:
        return {}, text

    # 解析头部每一行的 key: value。
    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            metadata[key.strip()] = value.strip()

    # 正文是闭合 --- 之后的剩余行。
    body = "\n".join(lines[end_index + 1 :]).strip()
    return metadata, body


__all__ = ["NexaResourcePaths", "ResourceError", "parse_markdown_resource"]
