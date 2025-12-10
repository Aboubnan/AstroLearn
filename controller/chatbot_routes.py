# controller/chatbot_routes.py

from flask import Blueprint, request, jsonify
from model.api_utils import call_hf_api # Import de la fonction d'appel IA

# Création du Blueprint
chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """Point de terminaison API pour le chatbot (appelé par AJAX)."""
    
    try: # Début du bloc de gestion d'erreurs global
        
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({"error": "Message utilisateur manquant"}), 400
        
        system_prompt = "Act as an expert astrophysicist and provide a concise, factual answer about astronomy. Respond in French. Do not mention that you are an AI, a model or a bot."
        
        # Appel simplifié qui renvoie le texte de la réponse (ou le texte de l'erreur)
        # Ceci peut lever une exception si l'API est injoignable
        ai_response_text = call_hf_api(user_message, system_prompt)
        
        # Si le texte renvoyé contient un mot clé d'erreur (provenant de api_utils.py), on le traite comme une erreur
        if "Erreur" in ai_response_text or "Token" in ai_response_text:
            return jsonify({
                "error": ai_response_text
            }), 500 # Renvoie un statut d'erreur si c'est un message d'erreur
            
        
        # Si ce n'est pas une erreur, renvoie la réponse propre
        return jsonify({
            "response": ai_response_text
        })
            
    except Exception as e:
        # Cette exception attrape toutes les erreurs non gérées ci-dessus (ex: problème de connexion)
        print(f"Erreur dans api_chatbot: {e}")
        return jsonify({"error": "Une erreur inattendue s'est produite lors du traitement de l'IA (voir console serveur)."}), 500