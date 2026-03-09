// static/js/main.js - VERSION CORRIGÉE ET AMÉLIORÉE

document.addEventListener('DOMContentLoaded', () => {
    console.log("✅ Main.js chargé");
    
    // Éléments du chatbot
    const openBtn = document.getElementById('chatbot-open-btn');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const clearBtn = document.getElementById('chatbot-clear-btn');
    const chatWindow = document.getElementById('chatbot-window');
    const chatForm = document.getElementById('chatbot-form');
    const chatInput = document.getElementById('chatbot-input');
    const messagesContainer = document.getElementById('chatbot-messages');
    const loadingIndicator = document.getElementById('chatbot-loading');

    // Vérification que les éléments existent
    if (!openBtn || !closeBtn || !chatWindow || !chatForm || !chatInput || !messagesContainer) {
        console.warn("⚠️ Certains éléments du chatbot sont manquants");
        return;
    }

    // État du chatbot
    let conversationHistory = [];
    const maxHistoryLength = 10;

    // Questions suggérées
    const suggestedQuestions = [
        "Quelle est la température du Soleil ?",
        "Combien de lunes a Jupiter ?",
        "Qu'est-ce qu'une supernova ?",
        "Pourquoi Mars est-elle rouge ?",
        "Comment se forment les galaxies ?"
    ];

    // Initialisation
    loadConversationHistory();

    // 1. Gestion de l'ouverture/fermeture de la fenêtre
    openBtn.addEventListener('click', () => {
        chatWindow.classList.remove('hidden');
        openBtn.classList.add('hidden');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        chatInput.focus();
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.classList.add('hidden');
        openBtn.classList.remove('hidden');
    });

    // Bouton effacer l'historique
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Voulez-vous vraiment effacer tout l\'historique de conversation ?')) {
                conversationHistory = [];
                localStorage.removeItem('astrolearn_chat_history');
                messagesContainer.innerHTML = '';
                displaySuggestions();
                console.log("🗑️ Historique effacé");
            }
        });
    }

    // Afficher les suggestions si pas d'historique
    function displaySuggestions() {
        const suggestionsHTML = `
            <div class="suggestions-container">
                <div class="message ai-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">
                            Bonjour ! 👋 Je suis <strong>AstroIA</strong>, votre assistant virtuel spécialisé en astronomie.
                            <br><br>
                            Posez-moi n'importe quelle question sur l'univers, ou choisissez parmi ces suggestions :
                        </div>
                    </div>
                </div>
                <div class="suggestions-buttons">
                    ${suggestedQuestions.map((q, i) => 
                        `<button class="suggestion-btn" data-question="${q}">
                            <i class="fas fa-lightbulb"></i> ${q}
                        </button>`
                    ).join('')}
                </div>
            </div>
        `;
        
        messagesContainer.innerHTML = suggestionsHTML;

        // Ajouter les événements aux boutons de suggestion
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.getAttribute('data-question');
                chatInput.value = question;
                chatForm.dispatchEvent(new Event('submit'));
            });
        });
    }

    // Fonction pour ajouter un message à la fenêtre
    function addMessage(text, sender) {
        // Supprimer les suggestions si présentes
        const suggestions = messagesContainer.querySelector('.suggestions-container');
        if (suggestions) {
            suggestions.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`, 'message-fade-in');
        
        let avatar;
        if (sender === 'user') {
            avatar = '<i class="fas fa-user"></i>';
        } else if (sender === 'ai') {
            avatar = '<i class="fas fa-robot"></i>';
        } else {
            avatar = '<i class="fas fa-exclamation-triangle"></i>';
        }

        // Formatage du texte
        let formattedText = text.replace(/\n/g, '<br>');
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');

        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-text">${formattedText}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        // Scroll automatique avec animation
        setTimeout(() => {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    // Indicateur de frappe
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message ai-message message-fade-in';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Obtenir l'heure actuelle
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    // Sauvegarder l'historique
    function saveConversationHistory() {
        try {
            if (conversationHistory.length > maxHistoryLength * 2) {
                conversationHistory = conversationHistory.slice(-maxHistoryLength * 2);
            }
            localStorage.setItem('astrolearn_chat_history', JSON.stringify(conversationHistory));
        } catch (e) {
            console.error('Erreur sauvegarde historique:', e);
        }
    }

    // Charger l'historique
    function loadConversationHistory() {
        try {
            const saved = localStorage.getItem('astrolearn_chat_history');
            if (saved) {
                conversationHistory = JSON.parse(saved);
                
                if (conversationHistory.length > 0) {
                    conversationHistory.forEach(msg => {
                        if (msg.role === 'user') {
                            addMessage(msg.content, 'user');
                        } else if (msg.role === 'assistant') {
                            addMessage(msg.content, 'ai');
                        }
                    });
                } else {
                    displaySuggestions();
                }
            } else {
                displaySuggestions();
            }
        } catch (e) {
            console.error('Erreur chargement historique:', e);
            displaySuggestions();
        }
    }

    // 2. Gestion de l'envoi du formulaire via AJAX
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();

        console.log("📤 Envoi du message:", message);

        // Validation
        if (!message) {
            console.warn("⚠️ Message vide");
            return;
        }

        if (message.length > 500) {
            addMessage('❌ Message trop long (max 500 caractères)', 'error');
            return;
        }

        // Ajouter le message de l'utilisateur
        addMessage(message, 'user');
        chatInput.value = '';

        // Sauvegarder dans l'historique
        conversationHistory.push({
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        });

        // Afficher l'indicateur de frappe
        showTypingIndicator();

        // Préparer le payload
        const payload = { 
            message: message
        };

        // Ajouter l'historique si disponible
        if (conversationHistory.length > 1) {
            const history = conversationHistory.slice(-6, -1).map(msg => ({
                role: msg.role,
                content: msg.content
            }));
            if (history.length > 0) {
                payload.history = history;
            }
        }

        console.log("📤 Payload envoyé:", payload);
        
        // Appel API Flask
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            console.log("📥 Réponse reçue, status:", response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("📥 Données reçues:", data);
            
            hideTypingIndicator();
            
            if (data.response) {
                addMessage(data.response, 'ai');
                
                // Sauvegarder dans l'historique
                conversationHistory.push({
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date().toISOString()
                });
                
                saveConversationHistory();
                
            } else if (data.error) {
                addMessage(`❌ ${data.error}`, 'error');
            }
        })
        .catch(error => {
            hideTypingIndicator();
            console.error('❌ Erreur Fetch:', error);
            addMessage('❌ Erreur de connexion au serveur.', 'error');
        });
    });

    // Raccourci clavier ESC pour fermer
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !chatWindow.classList.contains('hidden')) {
            chatWindow.classList.add('hidden');
            openBtn.classList.remove('hidden');
        }
    });
});