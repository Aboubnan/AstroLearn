# tests/test_chatbot_service.py
from unittest.mock import patch
import pytest

from model.chatbot_service import AstroIAChatbot


def test_ask_rejects_empty_message():
    chatbot = AstroIAChatbot()
    with pytest.raises(ValueError):
        chatbot.ask("   ")


def test_ask_rejects_message_too_long():
    chatbot = AstroIAChatbot()
    with pytest.raises(ValueError):
        chatbot.ask("a" * (AstroIAChatbot.MAX_MESSAGE_LENGTH + 1))


@patch("model.chatbot_service.call_gemini_api")
def test_ask_returns_sanitized_response(mock_call_gemini_api):
    mock_call_gemini_api.return_value = (
        "  La Lune est le seul satellite naturel de la Terre. "
    )

    chatbot = AstroIAChatbot()
    response = chatbot.ask("C'est quoi la Lune ?")

    assert response == "La Lune est le seul satellite naturel de la Terre."


@patch("model.chatbot_service.call_gemini_api")
def test_ask_truncates_overly_long_response(mock_call_gemini_api):
    mock_call_gemini_api.return_value = "x" * (AstroIAChatbot.MAX_RESPONSE_LENGTH + 100)

    chatbot = AstroIAChatbot()
    response = chatbot.ask("Question")

    assert len(response) == AstroIAChatbot.MAX_RESPONSE_LENGTH
    assert response.endswith("...")


@patch("model.chatbot_service.call_gemini_api")
def test_ask_raises_runtime_error_when_api_returns_nothing(mock_call_gemini_api):
    mock_call_gemini_api.return_value = None

    chatbot = AstroIAChatbot()
    with pytest.raises(RuntimeError):
        chatbot.ask("Question")


@patch("model.chatbot_service.call_gemini_api")
def test_ask_sends_only_last_five_history_messages(mock_call_gemini_api):
    mock_call_gemini_api.return_value = "Réponse"
    history = [{"role": "user", "content": str(i)} for i in range(8)]

    chatbot = AstroIAChatbot(history=history)
    chatbot.ask("Question")

    _, kwargs = mock_call_gemini_api.call_args
    assert len(kwargs["history"]) == AstroIAChatbot.MAX_HISTORY_MESSAGES
    assert kwargs["history"][-1]["content"] == "7"
