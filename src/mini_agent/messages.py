"""Core message types shared by all layers.

Module 1 of the learning guide: the provider-neutral data structures. Start
minimal (a dataclass and helpers); Tau grows these into Pydantic block-based
models later.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserMessage:
    """A user turn: plain text content for now."""

    content: str

    @property
    def text(self) -> str:
        return self.content


def message_text(message: object) -> str:
    """Return the user-visible text of a message."""
    if isinstance(message, UserMessage):
        return message.text
    return str(message)


__all__ = ["UserMessage", "message_text"]
