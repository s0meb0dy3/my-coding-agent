"""NEXA 的 TUI 界面。

- state.py / adapter.py：纯逻辑，不依赖 Textual，可脱离终端测试。
- app.py：Textual 渲染层，把 TuiState 画到屏幕。
"""

from nexa_coding.tui.app import NexaTuiApp

__all__ = ["NexaTuiApp"]
