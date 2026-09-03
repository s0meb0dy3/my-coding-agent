"""mini_agent: the portable brain — messages, tools, and (soon) the loop.

Owns the provider-neutral data structures and the agent loop. Pure: no CLI,
no Textual/Rich, no local config paths. mini_coding builds the app on top.
"""

from .messages import (
    AssistantMessage,
    Message,
    TextContent,
    ToolCall,
    ToolResultMessage,
    UserMessage,
    WireModel,
    message_text,
)
from .tools import (
    AgentTool,
    JsonSchema,
    ToolExecutor,
    make_executor,
    parse_tool_arguments,
    tool_schema,
    validate_tool_arguments,
    wrap_tool,
)
from .types import JSONValue

__all__ = [
    "AgentTool",
    "AssistantMessage",
    "JSONValue",
    "JsonSchema",
    "Message",
    "TextContent",
    "ToolCall",
    "ToolExecutor",
    "ToolResultMessage",
    "UserMessage",
    "WireModel",
    "make_executor",
    "message_text",
    "parse_tool_arguments",
    "tool_schema",
    "validate_tool_arguments",
    "wrap_tool",
]
