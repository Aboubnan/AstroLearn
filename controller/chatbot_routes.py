# controller/chatbot_routes.py

from typing import Any, Dict, Optional, Tuple, Union
from flask import Blueprint, request, jsonify, Response

from model.chatbot_service import AstroIAChatbot

# Blueprint creation
chatbot_bp = Blueprint("chatbot_bp", __name__)


@chatbot_bp.route("/api/chatbot", methods=["POST"])
def api_chatbot() -> Union[Response, Tuple[Response, int]]:
    """
    API endpoint for the AstroIA chatbot using Gemini 2.5 Flash.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Format JSON requis"}), 400

        data: Optional[Dict[str, Any]] = request.get_json()
        if data is None:
            return jsonify({"error": "Aucune donnée fournie"}), 400

        chatbot = AstroIAChatbot(history=data.get("history", []))

        try:
            ai_response_text = chatbot.ask(data.get("message", ""))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({"response": ai_response_text, "status": "success"}), 200

    except Exception as e:
        print(f"❌ Erreur inattendue dans api_chatbot: {e}")
        return jsonify({"error": "Une erreur technique est survenue."}), 500
