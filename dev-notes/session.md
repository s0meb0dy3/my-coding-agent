# Session 层说明

持久化会话层，位于 `src/nexa_agent/session/`。append-only JSONL 账本：会话记录只追加、不改写，可随时读回、回放成会话状态。

## 文件职责

| 文件 | 职责 |
| --- | --- |
| `__init__.py` | 汇总导出 5 个子模块的公开 API |
| `entries.py` | 账本条目模型：`BaseEntry`（`id` / `parent_id` / `type`）+ 3 种子类（`MessageEntry` / `ModelChangeEntry` / `LabelEntry`），`type` 作判别字段 |
| `jsonl.py` | 条目 ↔ 一行的序列化：`entry_to_line` / `entry_from_line`（未知 type 返回 `None`，坏 JSON 抛带行号的 `JsonlLineError`） |
| `storage.py` | 磁盘存取：`JsonlStorage.append`（建目录、追加一行）/ `read_all`（缺文件返回空列表、坏行跳过）。只追加绝不改写 |
| `tree.py` | 历史树：`path_to_entry(entries, leaf_id)` 沿 `parent_id` 走回根再反转，父节点悬空抛 `TreeError` |
| `memory.py` | 回放：`SessionState`（messages / model / label）+ `from_entries(entries, leaf_id=None)`，把条目重演成状态 |

## 三种条目

- `MessageEntry` — 一条会话消息，直接内嵌 `message: AgentMessage`（复用 role 判别），回放时原样取出
- `ModelChangeEntry` — 换模型，只记新状态 `model`（可带 `provider`），回放时覆盖
- `LabelEntry` — 给会话打标签，回放时覆盖 `label`

## 数据流

```text
AgentHarness 事件 → append() 逐条追加到 .jsonl
                       ↓（重新启动）
                   read_all() 读回全部条目
                       ↓
                   SessionState.from_entries(entries, leaf_id?)
                       回放成 messages / model / label
```

## 测试

`tests/test_session.py`：5 个不变量（追加不覆盖、顺序保持、树路径、坏行容忍、回放正确）+ leaf_id 子路径用例。

## 关键约定

- JSONL 序列化用 `model_dump_json(exclude_none=True)`：值为 None 的字段（如 `parent_id`）不写进文件
- `Entry` 是 PEP 695 类型别名，不能直接 `model_validate`，须经 `TypeAdapter(Entry)`（见 `jsonl.py` 的 `_ENTRY_ADAPTER`）
- 当前只支持线性追加；`parent_id` 已为将来分支（如 git commit 链）预留结构
