"""mini_agent: the portable brain — messages, tools, and (soon) the loop.

Owns the provider-neutral data structures and the agent loop. Pure: no CLI,
no Textual/Rich, no local config paths. mini_coding builds the app on top.
"""

from .messages import (
    AssistantMessage,
    Message,
    ToolCall,
    ToolResultMessage,
    UserMessage,
    message_from_dict,
    message_from_json,
    message_text,
    message_to_dict,
    message_to_json,
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

__all__ = [
    "AgentTool",
    "AssistantMessage",
    "JsonSchema",
    "Message",
    "ToolCall",
    "ToolExecutor",
    "ToolResultMessage",
    "UserMessage",
    "make_executor",
    "message_from_dict",
    "message_from_json",
    "message_text",
    "message_to_dict",
    "message_to_json",
    "parse_tool_arguments",
    "tool_schema",
    "validate_tool_arguments",
    "wrap_tool",
]
