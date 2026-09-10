"""会话账本的磁盘存储：只追加，绝不改写。

JsonlStorage 把 entry 一行行追加到一个 JSONL 文件里：
- 文件不存在时自动创建，父目录不存在时自动创建。
- 永远用追加模式打开，已有的内容不会被覆盖。
- read_all 缺文件时返回空列表，坏行跳过（未知 type / 格式错）。
"""

from __future__ import annotations

from pathlib import Path

from nexa_agent.session.entries import Entry
from nexa_agent.session.jsonl import JsonlLineError, entry_from_line, entry_to_line


class JsonlStorage:
    """把条目以 JSONL 形式追加到磁盘文件。"""

    def __init__(self, path: str | Path) -> None:
        """指定账本文件路径。

        Args:
            path: JSONL 文件路径。父目录不必预先存在，append 时会自动创建。
        """
        self._path = Path(path)

    @property
    def path(self) -> Path:
        """账本文件的路径。"""
        return self._path

    def append(self, entry: Entry) -> None:
        """把一条条目追加到账本末尾。

        文件不存在会先创建父目录和文件；永远以追加模式打开，
        因此绝不改写已有内容。
        """

        # 确保父目录存在，避免文件不存在时创建失败。
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # "a" 表示追加模式：指针在文件末尾，只写不覆盖。
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(entry_to_line(entry))
            handle.write("\n")

    def read_all(self) -> list[Entry]:
        """读取账本里全部条目，按写入顺序返回。

        文件不存在时返回空列表；遇到无法解析的行（JSON 格式错或
        未知 type）时跳过，不中断整体读取。
        """

        if not self._path.exists():
            return []

        entries: list[Entry] = []
        # 逐行读取，行号从 1 开始，用于报错定位。
        with self._path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                try:
                    entry = entry_from_line(line, line_no)
                except JsonlLineError:
                    # JSON 格式错：跳过这一行，继续读后面的。
                    continue
                if entry is not None:
                    entries.append(entry)
        return entries


__all__ = ["JsonlStorage"]
