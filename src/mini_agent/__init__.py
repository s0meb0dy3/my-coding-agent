"""mini_ai: the provider layer — how we talk to models.

Owns network, streaming, and provider-specific protocols (the "ears and mouth").
Never decides what the agent should do next.
"""

from .messages import UserMessage, message_text

__all__ = ["UserMessage", "message_text"]
