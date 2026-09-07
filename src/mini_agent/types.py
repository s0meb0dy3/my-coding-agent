"""Shared low-level types for my-coding-agent portable agent layer."""

from __future__ import annotations

# Pydantic needs PEP 695 named recursive aliases for JSON-like values.
type JSONPrimitive = str | int | float | bool | None # One Json could be a str, int, float, bool, or None.
type JSONValue = JSONPrimitive | list[JSONValue] | dict[str, JSONValue]
type JSONObject = dict[str, JSONValue]
