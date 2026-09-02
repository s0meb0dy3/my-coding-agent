"""Module 1 (types) / module 0 acceptance: message round-trips."""

from mini_agent import UserMessage, message_text


def test_user_message_holds_text() -> None:
    msg = UserMessage(content="hello")
    assert msg.content == "hello"
    assert msg.text == "hello"


def test_user_message_is_hashable_immutable() -> None:
    msg = UserMessage(content="hello")
    msg2 = UserMessage(content="hello")
    assert msg == msg2
    assert hash(msg) == hash(msg2)


def test_message_text_returns_content() -> None:
    assert message_text(UserMessage(content="hi")) == "hi"
