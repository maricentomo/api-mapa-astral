// Chat simples para páginas internas
document.addEventListener('DOMContentLoaded', function () {
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatHistory = document.getElementById('chat-history');

    const API_URL = 'https://api-mapa-astral-production.up.railway.app/chat';
    let messageHistory = [];

    // Função para adicionar mensagem
    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content user-message">
                    <p>${escapeHtml(content)}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content ai-message">
                    ${formatMarkdown(content)}
                </div>
            `;
        }

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Função para enviar mensagem
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Mostrar mensagem do usuário
        addMessage('user', message);
        chatInput.value = '';

        // Adicionar ao histórico
        messageHistory.push({ role: 'user', content: message });

        // Mostrar indicador de digitação
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-indicator';
        typingDiv.innerHTML = '<div class="message-content ai-message"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
        chatHistory.appendChild(typingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        try {
            // Chamar API
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    history: messageHistory.slice(0, -1) // Não incluir mensagem atual
                })
            });

            // Remover indicador de digitação
            typingDiv.remove();

            if (!response.ok) {
                throw new Error('Erro ao conectar com a IA');
            }

            const data = await response.json();
            addMessage('assistant', data.response);

            // Adicionar resposta ao histórico
            messageHistory.push({ role: 'assistant', content: data.response });

        } catch (error) {
            typingDiv.remove();
            addMessage('assistant', 'Desculpe, ocorreu um erro. Tente novamente.');
            console.error('Erro:', error);
        }
    }

    // Event listeners
    if (chatSend && chatInput) {
        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Utilitários
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    function formatMarkdown(text) {
        return text
            .replace(/### (.*?)(\n|$)/g, '<h3>$1</h3>')
            .replace(/## (.*?)(\n|$)/g, '<h2>$1</h2>')
            .replace(/# (.*?)(\n|$)/g, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.)/, '<p>$1')
            .replace(/(.)$/, '$1</p>');
    }
});
