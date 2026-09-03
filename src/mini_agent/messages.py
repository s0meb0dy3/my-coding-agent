"""Core message types shared by all layers.

Module 1 of the learning guide: the provider-neutral data structures every
layer speaks. Start minimal — dataclasses and JSON — before growing into
Pydantic block-based models like Tau's.

Layering rule: nothing here decides *what the agent should do next*; these
types only describe what a conversation contains.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A request from the assistant to run one tool."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UserMessage:
    """A user turn: plain text content for now."""

    role: ClassVar[str] = "user"
    content: str

    @property
    def text(self) -> str:
        return self.content


@dataclass(frozen=True, slots=True)
class AssistantMessage:
    """An assistant turn: text plus any tool calls it wants to make."""

    role: ClassVar[str] = "assistant"
    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()

    @property
    def text(self) -> str:
        return self.content


@dataclass(frozen=True, slots=True)
class ToolResultMessage:
    """The result of running one tool call, keyed back to it by id."""

    role: ClassVar[str] = "toolResult"
    tool_call_id: str
    tool_name: str
    content: str
    is_error: bool = False
    details: dict[str, Any] | None = None

    @property
    def text(self) -> str:
        return self.content


# Every layer's message is one of these three (a union tagged by role).
type Message = UserMessage | AssistantMessage | ToolResultMessage


def message_to_dict(message: Message) -> dict[str, Any]:
    """Convert a message to a plain dict tagged with its role."""
    data = asdict(message)
    data["role"] = message.role
    return data


def message_from_dict(data: dict[str, Any]) -> Message:
    """Build a message from a role-tagged dict; unknown roles fail loudly."""
    data = dict(data)
    role = data.pop("role", None)
    if role == "user":
        return UserMessage(**data)
    if role == "assistant":
        calls = data.pop("tool_calls", ()) or ()
        tool_calls = tuple(ToolCall(**call) for call in calls)
        return AssistantMessage(**data, tool_calls=tool_calls)
    if role == "toolResult":
        return ToolResultMessage(**data)
    raise ValueError(f"unknown message role: {role!r}")


def message_to_json(message: Message) -> str:
    """Serialize a message to one JSON line, safe for an append-only transcript."""
    return json.dumps(message_to_dict(message), ensure_ascii=False)


def message_from_json(line: str) -> Message:
    """Parse one JSON line back into a message; raises on corrupt input."""
    data = json.loads(line)
    if not isinstance(data, dict):
        raise ValueError("message JSON must be an object")
    return message_from_dict(data)


def message_text(message: Message) -> str:
    """Return the user-visible text of any message."""
    return message.text


__all__ = [
    "AssistantMessage",
    "Message",
    "ToolCall",
    "ToolResultMessage",
    "UserMessage",
    "message_from_dict",
    "message_from_json",
    "message_text",
    "message_to_dict",
    "message_to_json",
]
