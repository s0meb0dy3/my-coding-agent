"""提示模板（prompt template）的加载与渲染。

提示模板是"快捷输入"：一个 markdown 文件，正文里用 {{ 变量名 }} 占位，
调用时填入变量值，生成最终 prompt。

Phase 9 只做最简版：{{ var }} 渲染，缺变量抛 ResourceError。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from nexa_coding.resources import NexaResourcePaths, ResourceError, parse_markdown_resource

# 匹配 {{ 变量名 }} 占位符。
_VARIABLE_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")


@dataclass(frozen=True)
class PromptTemplate:
    """一个提示模板。

    Attributes:
        name: 模板名（不含 .md 后缀）。
        path: 模板文件路径。
        template: 模板正文，可能含 {{ var }} 占位符。
    """

    name: str
    path: Path
    template: str


def load_prompt_templates(paths: NexaResourcePaths) -> list[PromptTemplate]:
    """扫描提示模板目录，加载全部模板（<prompts_dir>/<name>.md）。"""

    prompts_dir = paths.prompts_dir
    if not prompts_dir.is_dir():
        return []

    templates: list[PromptTemplate] = []
    for file in sorted(prompts_dir.iterdir()):
        if file.is_file() and file.suffix == ".md":
            try:
                text = file.read_text(encoding="utf-8")
            except OSError as error:
                raise ResourceError(f"无法读取提示模板 {file}: {error}") from error
            # 模板也可以带 frontmatter，但这里只保留正文。
            _, body = parse_markdown_resource(text)
            templates.append(PromptTemplate(name=file.stem, path=file, template=body))
    return templates


def render_prompt_template(template: PromptTemplate, variables: dict[str, str]) -> str:
    """渲染模板：把 {{ 变量名 }} 替换成 variables 里的值。

    Raises:
        ResourceError: 模板里出现了 variables 没提供的变量时抛出。
    """

    def _replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        if var_name not in variables:
            raise ResourceError(f"模板缺少变量 {var_name!r}")
        return variables[var_name]

    return _VARIABLE_PATTERN.sub(_replace, template.template)


__all__ = ["PromptTemplate", "load_prompt_templates", "render_prompt_template"]
