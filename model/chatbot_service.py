# model/chatbot_service.py

from typing import Dict, List, Optional
from model.api_utils import call_gemini_api


class AstroIAChatbot:
    """Assistant conversationnel AstroIA.

    Encapsule la validation des messages, la construction du contexte envoyé
    à Gemini (prompt système + historique tronqué) et le nettoyage de la
    réponse. La route Flask ne fait que traduire les exceptions levées ici en
    réponses HTTP.
    """

    MAX_MESSAGE_LENGTH = 500
    MAX_RESPONSE_LENGTH = 2000
    MAX_HISTORY_MESSAGES = 5

    SYSTEM_PROMPT = (
        "Tu es AstroIA, un assistant virtuel expert en astronomie.\n"
        "Réponds toujours en Français, sois enthousiaste, concis (3-4 phrases) "
        "et utilise des emojis (🪐, ✨).\n"
        "N'utilise jamais de termes techniques sans les expliquer par une analogie simple."
    )

    def __init__(self, history: Optional[List[Dict[str, str]]] = None) -> None:
        self._history: List[Dict[str, str]] = history or []

    @property
    def history(self) -> List[Dict[str, str]]:
        return list(self._history)

    def ask(self, user_message: str) -> str:
        """Valide `user_message`, interroge Gemini et renvoie une réponse nettoyée.

        Lève ValueError si le message est vide ou trop long, RuntimeError si
        l'IA ne renvoie aucune réponse exploitable.
        """
        message = (user_message or "").strip()
        if not message:
            raise ValueError("Message vide")
        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Message trop long (max {self.MAX_MESSAGE_LENGTH} caractères)"
            )

        history_start = max(0, len(self._history) - self.MAX_HISTORY_MESSAGES)
        raw_response = call_gemini_api(
            user_input=message,
            system_instruction=self.SYSTEM_PROMPT,
            history=self._history[history_start:],
        )

        if not raw_response:
            raise RuntimeError(
                "L'IA n'a pas pu générer de réponse. Réessaye dans un instant."
            )

        return self._sanitize(raw_response)

    def _sanitize(self, response: str) -> str:
        response = response.strip()
        if len(response) > self.MAX_RESPONSE_LENGTH:
            response = response[: self.MAX_RESPONSE_LENGTH - 3] + "..."
        return response
