"""AgentTool: the contract for tools the loop can execute.

Module 1: a tool is a schema (for the model) plus an async executor (for us).
The loop only ever sees AgentTool; concrete tools like read/write/bash belong
to the coding layer (mini_coding) and are built on top of this.
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

# An async executor: takes parsed keyword arguments, returns the result text.
ToolExecutor = Callable[..., Awaitable[Any]]

# JSON-Schema subset describing the tool's arguments for the model.
JsonSchema = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class AgentTool:
    """A tool exposed to the agent loop.

    properties / required are the JSON Schema subset the model sees; executor
    is the code we run. Validation happens *before* the executor is called.
    """

    name: str
    description: str
    properties: JsonSchema = field(default_factory=dict)
    required: tuple[str, ...] = ()
    executor: ToolExecutor | None = None


def tool_schema(tool: AgentTool) -> dict[str, Any]:
    """The OpenAI-style function schema sent to the model."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": dict(tool.properties),
                "required": list(tool.required),
            },
        },
    }


def parse_tool_arguments(arguments: object) -> dict[str, Any]:
    """Parse tool arguments from the model (string or dict) into a dict.

    Raises a clear error on malformed input; the loop surfaces that error back
    to the model instead of crashing.
    """
    if isinstance(arguments, dict):
        return arguments
    if not isinstance(arguments, str):
        got = type(arguments).__name__
        raise ValueError(f"tool arguments must be a JSON string or dict, got {got}")
    text = arguments.strip()
    if not text:
        return {}
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("tool arguments JSON must be an object")
    return parsed


def validate_tool_arguments(arguments: Mapping[str, Any], properties: JsonSchema) -> None:
    """Validate parsed arguments against the tool's schema (best-effort).

    Covers the common cases a model gets wrong; full JSON Schema validation is
    deferred until a real validator is added.
    """
    for name, expected in properties.items():
        if name not in arguments:
            continue
        _require_type(name, arguments[name], expected.get("type"))


def _require_type(name: str, value: object, expected: object) -> None:
    """Raise if *value* is not compatible with the schema's *expected* type."""
    if expected == "string" and not isinstance(value, str):
        raise ValueError(f"argument {name!r} must be a string, got {type(value).__name__}")
    if expected == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
        raise ValueError(f"argument {name!r} must be a number, got {type(value).__name__}")


def make_executor(fn: Callable[..., Any]) -> ToolExecutor:
    """Wrap a sync function into an async executor (awaitable result).

    Used for simple pure tools in tests and demos.
    """
    if inspect.iscoroutinefunction(fn):
        return fn  # type: ignore[return-value]

    async def run(**kwargs: Any) -> Any:
        return fn(**kwargs)

    return run


def wrap_tool(
    name: str,
    fn: Callable[..., Any],
    description: str,
    properties: JsonSchema,
    required: tuple[str, ...] = (),
) -> AgentTool:
    """Build an AgentTool from a plain function + schema description."""
    return AgentTool(
        name=name,
        description=description,
        properties=properties,
        required=required,
        executor=make_executor(fn),
    )


__all__ = [
    "AgentTool",
    "JsonSchema",
    "ToolExecutor",
    "make_executor",
    "parse_tool_arguments",
    "tool_schema",
    "validate_tool_arguments",
    "wrap_tool",
]
