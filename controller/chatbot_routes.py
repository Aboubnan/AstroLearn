# controller/chatbot_routes.py - VERSION AMÉLIORÉE

from flask import Blueprint, request, jsonify
from model.api_utils import call_hf_api

# Création du Blueprint
chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """
    Point de terminaison API pour le chatbot avec support de l'historique de conversation.
    
    Reçoit:
        - message (str): Message de l'utilisateur
        - history (list, optionnel): Historique des 5 derniers messages
    
    Retourne:
        - response (str): Réponse de l'IA
        - error (str): Message d'erreur en cas de problème
    """
    
    try:
        # Vérification du format JSON
        if not request.is_json:
            return jsonify({"error": "Format JSON requis"}), 400

        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_history = data.get('history', [])

        # Validation du message
        if not user_message:
            return jsonify({"error": "Message vide"}), 400
        
        if len(user_message) > 500:
            return jsonify({"error": "Message trop long (max 500 caractères)"}), 400
        
        # Construction du prompt système enrichi
        system_prompt = """Tu es AstroIA, un assistant virtuel expert en astronomie et astrophysique.

RÔLE:
- Réponds aux questions sur l'univers, les planètes, les étoiles, les galaxies, etc.
- Utilise un langage clair et pédagogique adapté à tous les niveaux
- Sois enthousiaste et passionné par l'astronomie

RÈGLES:
- Réponds TOUJOURS en français
- Sois concis (maximum 3-4 phrases pour les réponses simples)
- Utilise des analogies simples pour les concepts complexes
- Si tu ne sais pas, dis-le honnêtement
- Ne mentionne jamais que tu es une IA, un modèle ou un bot
- Ne parle pas de tes limitations techniques

FORMAT:
- Utilise des retours à la ligne pour aérer les réponses longues
- Mets en gras (**texte**) les termes importants
- Utilise des émojis occasionnels pour rendre la conversation vivante (🌟, 🪐, ✨, etc.)

EXEMPLES DE RÉPONSES:
Question: "Quelle est la température du Soleil ?"
Réponse: "Le **Soleil** a une température de surface d'environ **5 500°C** ☀️. Mais attention, son cœur est bien plus chaud : **15 millions de degrés** ! C'est là que se produit la fusion nucléaire qui nous donne lumière et chaleur."

Question: "C'est quoi un trou noir ?"
Réponse: "Un **trou noir** est une région de l'espace où la gravité est si intense que même la lumière ne peut s'en échapper 🌑. Imagine un aspirateur cosmique ultra-puissant ! Ils se forment généralement après l'effondrement d'étoiles massives."
"""

        # Construction du prompt avec contexte de conversation
        if conversation_history and len(conversation_history) > 0:
            # Créer un contexte à partir des derniers messages
            context_messages = []
            for msg in conversation_history[-5:]:  # Derniers 5 messages max
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role == 'user':
                    context_messages.append(f"Utilisateur: {content}")
                elif role == 'assistant':
                    context_messages.append(f"Tu as répondu: {content}")
            
            context = "\n".join(context_messages)
            full_prompt = f"""CONTEXTE DE LA CONVERSATION:
{context}

NOUVELLE QUESTION:
{user_message}

Réponds en tenant compte du contexte de la conversation précédente."""
        else:
            full_prompt = user_message
        
        # Appel à l'API Gemini
        ai_response_text = call_hf_api(full_prompt, system_prompt)
        
        # Gestion des erreurs provenant de l'API
        if not ai_response_text:
            return jsonify({
                "error": "L'IA n'a pas pu générer de réponse. Veuillez réessayer."
            }), 500
        
        # Vérification des messages d'erreur dans la réponse
        error_keywords = ["Erreur", "Token", "Invalid", "Failed", "bloquée", "filtre de sécurité"]
        if any(keyword in ai_response_text for keyword in error_keywords):
            return jsonify({
                "error": ai_response_text
            }), 500
        
        # Nettoyage de la réponse
        ai_response_text = ai_response_text.strip()
        
        # Limitation de la longueur de la réponse (sécurité)
        if len(ai_response_text) > 2000:
            ai_response_text = ai_response_text[:1997] + "..."
        
        # Succès - Retour de la réponse
        return jsonify({
            "response": ai_response_text,
            "tokens_used": len(full_prompt.split()) + len(ai_response_text.split())
        }), 200
            
    except ValueError as e:
        # Erreur de parsing JSON
        print(f"Erreur de validation dans api_chatbot: {e}")
        return jsonify({
            "error": "Données invalides"
        }), 400
        
    except Exception as e:
        # Erreur inattendue
        print(f"Erreur inattendue dans api_chatbot: {e}")
        return jsonify({
            "error": "Une erreur s'est produite. Veuillez réessayer dans quelques instants."
        }), 500


@chatbot_bp.route('/api/chatbot/suggestions', methods=['GET'])
def get_suggestions():
    """
    Retourne une liste de questions suggérées pour démarrer une conversation.
    """
    suggestions = [
        {
            "question": "Quelle est la température du Soleil ?",
            "category": "système_solaire"
        },
        {
            "question": "Combien de lunes a Jupiter ?",
            "category": "système_solaire"
        },
        {
            "question": "Qu'est-ce qu'une supernova ?",
            "category": "étoiles"
        },
        {
            "question": "Pourquoi Mars est-elle rouge ?",
            "category": "planètes"
        },
        {
            "question": "Comment se forment les galaxies ?",
            "category": "cosmologie"
        },
        {
            "question": "Qu'est-ce qu'un trou noir ?",
            "category": "objets_extrêmes"
        },
        {
            "question": "Pourquoi la Lune change-t-elle de forme ?",
            "category": "système_solaire"
        },
        {
            "question": "C'est quoi la Voie Lactée ?",
            "category": "galaxies"
        }
    ]
    
    return jsonify({"suggestions": suggestions}), 200


@chatbot_bp.route('/api/chatbot/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de l'état du chatbot.
    """
    return jsonify({
        "status": "operational",
        "service": "AstroIA Chatbot",
        "version": "2.0"
    }), 200