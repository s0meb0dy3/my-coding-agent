"""技能（skill）的加载、展开与索引。

一个技能是一段可复用的指令文本（markdown），放在技能目录下：
- <skills_dir>/<name>/SKILL.md
- 或 <skills_dir>/<name>.md

技能文件可用 frontmatter 声明 name / description；用户输入 /skill:name 参数
时，把技能正文 + 参数拼成一段展开文本塞给模型。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nexa_coding.resources import NexaResourcePaths, ResourceError, parse_markdown_resource


@dataclass(frozen=True)
class Skill:
    """一个已加载的技能。

    Attributes:
        name: 技能名，用于 /skill:name 触发。
        path: 技能文件路径。
        description: 一句话说明，来自 frontmatter，缺省用正文首行。
        content: 技能的正文 markdown。
    """

    name: str
    path: Path
    description: str
    content: str


def load_skills(paths: NexaResourcePaths) -> list[Skill]:
    """扫描技能目录，加载全部技能。

    支持两种布局：
    - <skills_dir>/<name>/SKILL.md
    - <skills_dir>/<name>.md

    Raises:
        ResourceError: 两种布局出现同名技能时抛出。
    """

    skills_dir = paths.skills_dir
    if not skills_dir.is_dir():
        return []

    # 先收集目录布局和文件布局的技能名，检测重名。
    skills_by_name: dict[str, Skill] = {}

    def _register(path: Path) -> None:
        name = _skill_name_from_path(path, skills_dir)
        if name in skills_by_name:
            raise ResourceError(f"技能重名：{name!r} 出现在 {path}")
        skills_by_name[name] = _load_skill_file(name, path)

    # 目录布局：<name>/SKILL.md
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.is_file():
                _register(skill_file)

    # 文件布局：<name>.md
    for file in sorted(skills_dir.iterdir()):
        if file.is_file() and file.suffix == ".md" and file.stem != "SKILL":
            _register(file)

    # 返回时按名字排序，保证输出稳定。
    return [skills_by_name[name] for name in sorted(skills_by_name)]


def expand_skill_command(text: str, skills: list[Skill]) -> str | None:
    """如果输入是 /skill:name 命令，返回展开后的技能文本。

    命中时返回带 <skill> 包裹的完整文本；否则返回 None。

    参数格式：/skill:name 附加参数（可选）。
    """

    stripped = text.strip()
    if not stripped.startswith("/skill:"):
        return None

    # 拆出命令头和参数："name 附加参数"。
    command, _, args = stripped.partition(" ")
    skill_name = command.removeprefix("/skill:").strip()

    if not skill_name:
        return None

    for skill in skills:
        if skill.name == skill_name:
            # 用 <skill> 包裹，让模型清楚这是一段指令 + 用户给的参数。
            return (
                f'<skill name="{skill.name}">\n'
                f"<instructions>\n{skill.content}\n</instructions>\n"
                f"<arguments>\n{args}\n</arguments>\n"
                f"</skill>"
            )
    return None


def build_skill_index(skills: list[Skill]) -> str:
    """生成"可用技能清单"，供系统提示词使用。"""

    if not skills:
        return ""
    lines = ["可用技能："]
    for skill in skills:
        lines.append(f"- {skill.name}: {skill.description}")
    return "\n".join(lines)


# ── 内部辅助 ─────────────────────────────────────────────────────────────────


def _skill_name_from_path(path: Path, skills_dir: Path) -> str:
    """从技能文件路径推导技能名。

    <skills_dir>/<name>/SKILL.md → <name>
    <skills_dir>/<name>.md        → <name>
    """

    relative = path.relative_to(skills_dir)
    if relative.name == "SKILL.md":
        return relative.parent.name
    return relative.stem


def _load_skill_file(name: str, path: Path) -> Skill:
    """读取一个技能文件，解析 frontmatter。"""

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ResourceError(f"无法读取技能文件 {path}: {error}") from error

    metadata, body = parse_markdown_resource(text)
    description = metadata.get("description") or _first_line(body)
    return Skill(name=name, path=path, description=description, content=body)


def _first_line(text: str) -> str:
    """取正文第一行作为缺省描述。"""

    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


__all__ = ["Skill", "build_skill_index", "expand_skill_command", "load_skills"]
