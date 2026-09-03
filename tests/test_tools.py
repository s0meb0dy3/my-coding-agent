"""Module 1 (tools) tests: schema, argument parsing, validation, execution."""

import pytest

from mini_agent import (
    AgentTool,
    parse_tool_arguments,
    tool_schema,
    validate_tool_arguments,
    wrap_tool,
)


def test_tool_schema_shape() -> None:
    tool = AgentTool(
        name="read",
        description="Read a file.",
        properties={"path": {"type": "string"}},
        required=("path",),
    )
    schema = tool_schema(tool)
    assert schema["type"] == "function"
    fn = schema["function"]
    assert fn["name"] == "read"
    assert fn["parameters"]["required"] == ["path"]


def test_parse_tool_arguments_accepts_string() -> None:
    assert parse_tool_arguments('{"path": "a.py"}') == {"path": "a.py"}


def test_parse_tool_arguments_accepts_dict() -> None:
    assert parse_tool_arguments({"path": "a.py"}) == {"path": "a.py"}


def test_parse_tool_arguments_empty_string_is_empty_dict() -> None:
    assert parse_tool_arguments("") == {}


def test_parse_tool_arguments_rejects_bad_json() -> None:
    with pytest.raises(ValueError):
        parse_tool_arguments("{not json")


def test_parse_tool_arguments_rejects_non_object_json() -> None:
    with pytest.raises(ValueError, match="must be an object"):
        parse_tool_arguments("[1, 2]")


def test_validate_arguments_requires_string_type() -> None:
    properties = {"path": {"type": "string"}}
    with pytest.raises(ValueError, match="must be a string"):
        validate_tool_arguments({"path": 123}, properties)


def test_validate_arguments_passes_correct_types() -> None:
    properties = {"path": {"type": "string"}, "max": {"type": "number"}}
    validate_tool_arguments({"path": "a.py", "max": 5}, properties)  # no raise


async def test_wrap_tool_executes_sync_function() -> None:
    tool = wrap_tool(
        name="greet",
        fn=lambda name: f"hello {name}",
        description="Greet someone.",
        properties={"name": {"type": "string"}},
        required=("name",),
    )
    assert tool.name == "greet"
    result = await tool.executor(name="world")  # type: ignore[call-arg]
    assert result == "hello world"


def test_agent_tool_value_equality() -> None:
    a = AgentTool(name="read", description="Read a file.")
    b = AgentTool(name="read", description="Read a file.")
    assert a == b
