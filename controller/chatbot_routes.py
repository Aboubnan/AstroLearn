# controller/chatbot_routes.py

from typing import List, Dict, Any, Optional, Tuple, Union
from flask import Blueprint, request, jsonify, Response
# On change l'import pour pointer vers ta nouvelle fonction Gemini
from model.api_utils import call_gemini_api 

# Blueprint creation
chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/api/chatbot', methods=['POST'])
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

        user_message: str = data.get('message', '').strip()
        conversation_history: List[Dict[str, str]] = data.get('history', [])

        # Validations de base
        if not user_message:
            return jsonify({"error": "Message vide"}), 400
        
        if len(user_message) > 500:
            return jsonify({"error": "Message trop long (max 500 caractères)"}), 400
        
        # System prompt (Ta version était excellente, on la garde !)
        system_prompt: str = """Tu es AstroIA, un assistant virtuel expert en astronomie.
        Réponds toujours en Français, sois enthousiaste, concis (3-4 phrases) et utilise des emojis (🪐, ✨).
        N'utilise jamais de termes techniques sans les expliquer par une analogie simple."""

        # Construction du contexte pour Gemini
        # On passe l'historique directement s'il existe
        ai_response_text: Optional[str] = call_gemini_api(
            user_input=user_message, 
            system_instruction=system_prompt,
            history=conversation_history[-5:] # On garde les 5 derniers échanges
        )
        
        if not ai_response_text:
            return jsonify({
                "error": "L'IA n'a pas pu générer de réponse. Réessaye dans un instant."
            }), 500
        
        # Nettoyage et limitation (Sécurité)
        ai_response_text = ai_response_text.strip()
        if len(ai_response_text) > 2000:
            ai_response_text = ai_response_text[:1997] + "..."
        
        return jsonify({
            "response": ai_response_text,
            "status": "success"
        }), 200
            
    except Exception as e:
        print(f"❌ Erreur inattendue dans api_chatbot: {e}")
        return jsonify({
            "error": "Une erreur technique est survenue."
        }), 500

# Les routes suggestions et health restent identiques...