"""Module 1 (types) tests: block-based messages and wire format.

These assert the *conventions* we deliberately copied from Tau's messages.py:
content is a list of blocks, tool calls are blocks in that list, tool results
key back to calls by id, and the wire format is camelCase JSON tagged by role.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from mini_agent import (
    AssistantMessage,
    Message,
    TextContent,
    ToolCall,
    ToolResultMessage,
    UserMessage,
    message_text,
)


def _call(**kwargs: object) -> ToolCall:
    return ToolCall.model_validate({"id": "c1", "name": "read", **kwargs})


# --- message construction and content ---


def test_user_message_holds_plain_string() -> None:
    msg = UserMessage(content="hello")
    assert msg.text == "hello"


def test_user_message_accepts_text_blocks() -> None:
    msg = UserMessage(content=[TextContent(text="hi"), TextContent(text=" there")])
    assert msg.text == "hi there"


def test_assistant_text_and_tool_call_are_one_content_list() -> None:
    # Order matters: text first, then the tool call, in a single ordered list.
    msg = AssistantMessage(
        content=[TextContent(text="let me read"), _call(arguments={"path": "a.py"})]
    )
    assert msg.text == "let me read"
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0].id == "c1"
    assert [b.type for b in msg.content] == ["text", "toolCall"]


def test_assistant_message_accepts_string_as_convenience() -> None:
    # Tau stores blocks, but accepts a plain string when constructing.
    msg = AssistantMessage(content="hi")
    assert msg.content == [TextContent(text="hi")]
    assert msg.tool_calls == ()


def test_tool_call_arguments_are_dict() -> None:
    call = _call(arguments={"path": "a.py"})
    assert call.arguments == {"path": "a.py"}
    assert call.type == "toolCall"


def test_tool_result_keys_back_to_call() -> None:
    result = ToolResultMessage(
        tool_call_id="c1", tool_name="read", content=[TextContent(text="# Heading")]
    )
    assert result.tool_call_id == "c1"
    assert result.text == "# Heading"
    assert not result.is_error


# --- wire format (camelCase aliases, role-tagged, discriminable) ---


def test_wire_format_is_camel_case() -> None:
    result = ToolResultMessage(
        tool_call_id="abc", tool_name="read", content=[TextContent(text="x")]
    )
    wire = result.model_dump_json()
    assert '"toolCallId"' in wire
    assert '"tool_call_id"' not in wire


def test_wire_format_round_trips() -> None:
    original = AssistantMessage(
        content=[TextContent(text="reading"), _call(arguments={"path": "a.py"})]
    )
    restored = AssistantMessage.model_validate_json(original.model_dump_json())
    assert restored == original


def test_messages_are_a_role_discriminated_union() -> None:
    by_role = {
        "user": UserMessage(content="hi"),
        "assistant": AssistantMessage(content="hi"),
        "toolResult": ToolResultMessage(tool_call_id="c1", tool_name="read"),
    }
    adapter = TypeAdapter(Message)
    for role, message in by_role.items():
        restored = adapter.validate_python(message.model_dump())
        assert restored == message
        assert restored.role == role


def test_unknown_role_json_fails_loudly() -> None:
    with pytest.raises(ValidationError):
        TypeAdapter(Message).validate_python({"role": "system", "content": "hi"})


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        UserMessage.model_validate({"content": "hi", "sneaky": True})


def test_message_text_covers_all_roles() -> None:
    assert message_text(UserMessage(content="u")) == "u"
    assert message_text(AssistantMessage(content="a")) == "a"
    assert message_text(ToolResultMessage(tool_call_id="1", tool_name="read", content="r")) == "r"
