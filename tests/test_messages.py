"""Module 1 (types) tests: message round-trips and tagging rules."""

import json

import pytest

from mini_agent import (
    AssistantMessage,
    ToolCall,
    ToolResultMessage,
    UserMessage,
    message_from_json,
    message_text,
    message_to_json,
)


def test_user_message_holds_text() -> None:
    msg = UserMessage(content="hello")
    assert msg.content == "hello"
    assert msg.text == "hello"


def test_assistant_message_carries_text_and_tool_calls() -> None:
    call = ToolCall(id="c1", name="read", arguments={"path": "README.md"})
    msg = AssistantMessage(content="let me read it", tool_calls=(call,))
    assert msg.text == "let me read it"
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0].id == "c1"


def test_tool_result_message_keys_back_to_call() -> None:
    call = ToolCall(id="c1", name="read", arguments={"path": "README.md"})
    result = ToolResultMessage(
        tool_call_id=call.id,
        tool_name=call.name,
        content="# Heading",
    )
    assert result.tool_call_id == "c1"
    assert result.text == "# Heading"
    assert not result.is_error


def test_messages_round_trip_through_json() -> None:
    original = [
        UserMessage(content="hi"),
        AssistantMessage(
            content="reading",
            tool_calls=(ToolCall(id="c1", name="read", arguments={"path": "a.py"}),),
        ),
        ToolResultMessage(tool_call_id="c1", tool_name="read", content="print(1)"),
    ]
    for message in original:
        restored = message_from_json(message_to_json(message))
        assert restored == message


def test_json_line_is_single_line_json() -> None:
    line = message_to_json(AssistantMessage(content="hi"))
    assert "\n" not in line
    assert line.startswith("{") and line.endswith("}")


def test_unknown_role_in_json_fails_loudly() -> None:
    with pytest.raises(ValueError, match="unknown message role"):
        message_from_json('{"role": "system", "content": "hi"}')


def test_corrupt_json_fails_loudly() -> None:
    with pytest.raises(json.JSONDecodeError):
        message_from_json("{not json")


def test_message_text_covers_all_message_types() -> None:
    assert message_text(UserMessage(content="u")) == "u"
    assert message_text(AssistantMessage(content="a")) == "a"
    assert message_text(ToolResultMessage(tool_call_id="1", tool_name="read", content="r")) == "r"
