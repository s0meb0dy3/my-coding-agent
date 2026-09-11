"""NEXA 的资源路径发现与 markdown 资源解析。

资源（resource）是指 agent 加载的本地知识文件：技能（skills）、提示模板
（prompt templates）等。本模块负责两件事：
- 决定资源从哪里找：用户级（~/.nexa、~/.agents）+ 项目级（<cwd>/.nexa、
  <cwd>/.agents）四级来源，按优先级递增排序，项目覆盖用户
- 解析一个 markdown 资源的 frontmatter（--- 包裹的 key: value 头部）

具体路径全部委托给 NexaPaths（单一真相源），这里不自算。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nexa_coding.paths import NexaPaths


class ResourceError(ValueError):
    """资源加载或解析出错时抛出。"""


@dataclass(frozen=True)
class NexaResourcePaths:
    """资源发现配置：从哪里、按什么优先级找资源。

    Attributes:
        cwd: 项目目录；为 None 时只发现用户级资源。
        paths: NexaPaths 实例；测试时可注入自定义家目录，默认用真实路径。
    """

    cwd: Path | None = None
    paths: NexaPaths = NexaPaths()

    def _paths(self) -> NexaPaths:
        """取委托的路径真相源。"""
        return self.paths

    @property
    def skills_dirs(self) -> tuple[Path, ...]:
        """技能目录元组，按优先级递增（后面的覆盖前面的）。

        1. ~/.nexa/skills          用户级
        2. ~/.agents/skills        用户级通用技能
        3. <cwd>/.nexa/skills      项目级
        4. <cwd>/.agents/skills    项目级团队共享（最高）
        """

        p = self._paths()
        dirs = [p.user_skills_dir, p.user_agents_skills_dir]
        if self.cwd is not None:
            dirs.append(p.project_skills_dir(self.cwd))
            dirs.append(p.project_agents_skills_dir(self.cwd))
        return tuple(dirs)

    @property
    def prompts_dirs(self) -> tuple[Path, ...]:
        """提示模板目录元组，优先级与 skills_dirs 一致。"""

        p = self._paths()
        dirs = [p.user_prompts_dir, p.user_agents_prompts_dir]
        if self.cwd is not None:
            dirs.append(p.project_prompts_dir(self.cwd))
            dirs.append(p.project_agents_prompts_dir(self.cwd))
        return tuple(dirs)


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
