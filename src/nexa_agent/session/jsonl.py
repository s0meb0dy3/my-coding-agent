"""条目 <-> JSONL 一行的双向序列化。

JSONL 就是"每行一个 JSON 对象"的文本文件。这里提供两个纯函数：
- entry_to_line:   把一条 entry 变成一行字符串（不含换行符）。
- entry_from_line: 把一行字符串解析回一条 entry。
"""

from __future__ import annotations

import json

from pydantic import TypeAdapter, ValidationError

from nexa_agent.session.entries import Entry


# 解析失败时统一抛出的异常类型：带行号，方便定位坏行。
class JsonlLineError(ValueError):
    """JSONL 某一行无法解析时抛出，message 里带行号。"""


# Entry 是 PEP 695 类型别名（type Entry = Annotated[...]），不能直接对别名
# 调用 model_validate / model_dump_json；TypeAdapter 正是为这类情况准备的，
# 它把一个任意类型包装成可校验、可序列化的适配器。模块级单例避免反复创建。
_ENTRY_ADAPTER: TypeAdapter[Entry] = TypeAdapter(Entry)


def entry_to_line(entry: Entry) -> str:
    """把一条 entry 序列化成一行 JSON 字符串。

    exclude_none=True 表示值为 None 的字段（例如 parent_id）不写进 JSON，
    避免每行都带一堆 "parentId": null。
    """

    return _ENTRY_ADAPTER.dump_json(entry, exclude_none=True).decode()


def entry_from_line(line: str, line_no: int) -> Entry | None:
    """把一行 JSON 字符串解析回一条 entry。

    Args:
        line: 文件里读到的原始行（可能带行尾换行符）。
        line_no: 这一行在文件中的行号（从 1 开始），用于报错定位。

    Returns:
        解析成功的 entry；遇到未知 type 的行返回 None（容忍跳过）。

    Raises:
        JsonlLineError: 这一行不是合法 JSON 时抛出，message 里带行号。
    """

    # strip() 去掉行尾换行符和空白，避免影响 JSON 解析。
    text = line.strip()
    # 空行直接跳过，不算错误。
    if not text:
        return None

    # 第一步：先按纯 JSON 解析，格式错误在这里暴露（带行号报错）。
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise JsonlLineError(f"第 {line_no} 行不是合法 JSON: {error}") from error

    # 第二步：按判别联合解析；未知 type 或字段不符在这里抛 ValidationError。
    # 这两种情况都属于"这一行我们看不懂"，统一容忍为 None，由调用方决定跳过。
    try:
        return _ENTRY_ADAPTER.validate_python(data)
    except ValidationError:
        return None


__all__ = ["JsonlLineError", "entry_from_line", "entry_to_line"]
