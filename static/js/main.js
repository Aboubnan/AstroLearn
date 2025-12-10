document.addEventListener('DOMContentLoaded', () => {
    const openBtn = document.getElementById('chatbot-open-btn');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const chatWindow = document.getElementById('chatbot-window');
    const chatForm = document.getElementById('chatbot-form');
    const chatInput = document.getElementById('chatbot-input');
    const messagesContainer = document.getElementById('chatbot-messages');
    const loadingIndicator = document.getElementById('chatbot-loading');

    // 1. Gestion de l'ouverture/fermeture de la fenêtre
    if (openBtn && closeBtn && chatWindow) {
        openBtn.addEventListener('click', () => {
            chatWindow.classList.remove('hidden');
            openBtn.classList.add('hidden');
            messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll en bas
            chatInput.focus();
        });

        closeBtn.addEventListener('click', () => {
            chatWindow.classList.add('hidden');
            openBtn.classList.remove('hidden');
        });
    }

    // Fonction pour ajouter un message à la fenêtre
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        // Sécurité: utiliser innerHTML pour gérer les retours à la ligne (\n) 
        // formatés par l'IA en les remplaçant par des <br>
        messageDiv.innerHTML = text.replace(/\n/g, '<br>'); 
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll automatique
    }

    // 2. Gestion de l'envoi du formulaire via AJAX
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();

            if (message) {
                addMessage(message, 'user');
                chatInput.value = '';
                loadingIndicator.classList.remove('hidden'); // Afficher le chargement
                
                // Appel API Flask au nouveau point de terminaison
                fetch('/api/chatbot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    // Envoie le message sous forme de JSON
                    body: JSON.stringify({ message: message })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    loadingIndicator.classList.add('hidden'); // Cacher le chargement
                    if (data.response) {
                        addMessage(data.response, 'ai');
                    } else if (data.error) {
                        // Affiche l'erreur renvoyée par le serveur
                        addMessage(`Erreur serveur : ${data.error}`, 'ai');
                    }
                })
                .catch(error => {
                    loadingIndicator.classList.add('hidden');
                    console.error('Erreur Fetch:', error);
                    addMessage('Erreur de connexion au serveur. Vérifiez la console pour les détails.', 'ai');
                });
            }
        });
    }
});