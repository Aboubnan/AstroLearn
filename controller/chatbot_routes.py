# controller/chatbot_routes.py

from typing import List, Dict, Any, Optional, Tuple, Union
from flask import Blueprint, request, jsonify, Response
from model.api_utils import call_hf_api

# Blueprint creation
chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def api_chatbot() -> Union[Response, Tuple[Response, int]]:
    """
    API endpoint for the chatbot with conversation history support.
    
    Expects JSON:
        - message (str): User's input message
        - history (list, optional): History of the last 5 messages
    
    Returns:
        - response (str): AI-generated answer
        - error (str): Error message if applicable
    """
    
    try:
        # Check JSON format
        if not request.is_json:
            return jsonify({"error": "JSON format required"}), 400

        data: Optional[Dict[str, Any]] = request.get_json()
        if data is None:
            return jsonify({"error": "No data provided"}), 400

        user_message: str = data.get('message', '').strip()
        conversation_history: List[Dict[str, str]] = data.get('history', [])

        # Message validation
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
        
        if len(user_message) > 500:
            return jsonify({"error": "Message too long (max 500 chars)"}), 400
        
        # System prompt definition (Professional Roleplay)
        system_prompt: str = """You are AstroIA, a virtual assistant expert in astronomy and astrophysics.

ROLE:
- Answer questions about the universe, planets, stars, galaxies, etc.
- Use clear and educational language suitable for all levels.
- Be enthusiastic and passionate about astronomy.

RULES:
- ALWAYS answer in French.
- Be concise (maximum 3-4 sentences for simple answers).
- Use simple analogies for complex concepts.
- If you don't know, say so honestly.
- Never mention that you are an AI, a model, or a bot.
- Do not talk about your technical limitations.

FORMAT:
- Use line breaks to air out long responses.
- Use bold (**text**) for important terms.
- Use occasional emojis (🌟, 🪐, ✨, etc.) to make the conversation lively.
"""

        # Building prompt with conversation context
        full_prompt: str = ""
        if conversation_history and len(conversation_history) > 0:
            # Create context from the last 5 messages
            context_messages: List[str] = []
            for msg in conversation_history[-5:]:
                role: str = msg.get('role', '')
                content: str = msg.get('content', '')
                if role == 'user':
                    context_messages.append(f"User: {content}")
                elif role == 'assistant':
                    context_messages.append(f"You replied: {content}")
            
            context: str = "\n".join(context_messages)
            full_prompt = (
                f"CONVERSATION CONTEXT:\n{context}\n\n"
                f"NEW QUESTION:\n{user_message}\n\n"
                "Answer while taking the previous context into account."
            )
        else:
            full_prompt = user_message
        
        # Calling the AI API (Gemini via api_utils)
        ai_response_text: Optional[str] = call_hf_api(full_prompt, system_prompt)
        
        # Handling API errors
        if not ai_response_text:
            return jsonify({
                "error": "The AI could not generate a response. Please try again."
            }), 500
        
        # Security check for error messages in AI response
        error_keywords: List[str] = [
            "Error", "Token", "Invalid", "Failed", "blocked", "safety filter"
        ]
        if any(keyword in ai_response_text for keyword in error_keywords):
            return jsonify({
                "error": ai_response_text
            }), 500
        
        # Cleaning the response
        ai_response_text = ai_response_text.strip()
        
        # Response length limitation (Security)
        if len(ai_response_text) > 2000:
            ai_response_text = ai_response_text[:1997] + "..."
        
        # Success - Returning response and meta-data
        return jsonify({
            "response": ai_response_text,
            "tokens_used": len(full_prompt.split()) + len(ai_response_text.split())
        }), 200
            
    except ValueError as e:
        print(f"Validation error in api_chatbot: {e}")
        return jsonify({"error": "Invalid data"}), 400
        
    except Exception as e:
        print(f"Unexpected error in api_chatbot: {e}")
        return jsonify({
            "error": "An error occurred. Please try again in a few moments."
        }), 500


@chatbot_bp.route('/api/chatbot/suggestions', methods=['GET'])
def get_suggestions() -> Tuple[Response, int]:
    """
    Returns a list of suggested questions to start a conversation.
    """
    suggestions: List[Dict[str, str]] = [
        {"question": "Quelle est la température du Soleil ?", "category": "solar_system"},
        {"question": "Combien de lunes a Jupiter ?", "category": "solar_system"},
        {"question": "Qu'est-ce qu'une supernova ?", "category": "stars"},
        {"question": "Pourquoi Mars est-elle rouge ?", "category": "planets"},
        {"question": "Comment se forment les galaxies ?", "category": "cosmology"},
        {"question": "Qu'est-ce qu'un trou noir ?", "category": "extreme_objects"},
        {"question": "Pourquoi la Lune change-t-elle de forme ?", "category": "solar_system"},
        {"question": "C'est quoi la Voie Lactée ?", "category": "galaxies"}
    ]
    
    return jsonify({"suggestions": suggestions}), 200


@chatbot_bp.route('/api/chatbot/health', methods=['GET'])
def health_check() -> Tuple[Response, int]:
    """
    Chatbot status check endpoint.
    """
    return jsonify({
        "status": "operational",
        "service": "AstroIA Chatbot",
        "version": "2.0"
    }), 200