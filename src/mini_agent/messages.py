"""Core message types shared by all layers.

Module 1 of the learning guide: the provider-neutral data structures every
layer speaks, modeled the way Tau models them — Pydantic, block-based content,
JSON aliases on the wire — but cut down to what a starter loop needs.

Keep these conventions (they match Tau's src/tau_agent/messages.py):
- content is a list of *blocks*, never a raw string; a tool call is just one
  kind of block (type="toolCall"). Text, thinking, images, and tool calls all
  live in that one ordered list.
- every message serializes to camelCase on the wire and is tagged by `role`;
  `Message` is a discriminated union on that role field.

What we deliberately omit for now: thinking/image blocks, usage accounting,
diagnostics, model metadata, and non-core message roles (bashExecution,
custom, branchSummary, compactionSummary). They come back when a module
needs them.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mini_agent.types import JSONValue


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


class WireModel(BaseModel):
    """Strict model with Python field names and JSON aliases on the wire."""

    model_config = ConfigDict(
        extra="forbid",
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        alias_generator=_to_camel,
    )


class TextContent(WireModel):
    """A plain-text content block."""

    type: Literal["text"] = "text"
    text: str


class ToolCall(WireModel):
    """A tool-use request block the assistant emits."""

    type: Literal["toolCall"] = "toolCall"
    id: str
    name: str
    arguments: dict[str, JSONValue] = Field(default_factory=dict)


class UserMessage(WireModel):
    role: Literal["user"] = "user"
    content: str | list[TextContent]

    @property
    def text(self) -> str:
        """The visible text of this message."""
        if isinstance(self.content, str):
            return self.content
        return "".join(block.text for block in self.content)


class AssistantMessage(WireModel):
    """An assistant turn: an ordered list of text and tool-call blocks."""

    role: Literal["assistant"] = "assistant"
    content: list[TextContent | ToolCall] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalize_string_content(cls, value: object) -> object:
        """Accept a plain string only as a construction convenience.

        The stored model and wire protocol are always block based. This keeps
        test construction terse without creating a second representation.
        """
        if isinstance(value, dict):
            data = dict(value)
            content = data.get("content")
            if isinstance(content, str):
                data["content"] = [TextContent(text=content)] if content else []
            return data
        return value

    @property
    def text(self) -> str:
        """The visible text of this message (tool-call blocks carry no text)."""
        return "".join(block.text for block in self.content if isinstance(block, TextContent))

    @property
    def tool_calls(self) -> tuple[ToolCall, ...]:
        return tuple(block for block in self.content if isinstance(block, ToolCall))


class ToolResultMessage(WireModel):
    """The result of running one tool call, keyed back to it by id."""

    role: Literal["toolResult"] = "toolResult"
    tool_call_id: str
    tool_name: str
    content: list[TextContent] = Field(default_factory=list)
    is_error: bool = False
    details: JSONValue = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_string_content(cls, value: object) -> object:
        """Accept a plain string only as a construction convenience."""
        if isinstance(value, dict):
            data = dict(value)
            content = data.get("content")
            if isinstance(content, str):
                data["content"] = [TextContent(text=content)] if content else []
            return data
        return value

    @property
    def text(self) -> str:
        return "".join(block.text for block in self.content)


type Message = Annotated[
    UserMessage | AssistantMessage | ToolResultMessage,
    Field(discriminator="role"),
]


def message_text(message: Message) -> str:
    """Return the user-visible text of any message."""
    return message.text


__all__ = [
    "AssistantMessage",
    "Message",
    "TextContent",
    "ToolCall",
    "ToolResultMessage",
    "UserMessage",
    "WireModel",
    "message_text",
]
