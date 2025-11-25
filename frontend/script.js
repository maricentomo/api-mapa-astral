// Page Navigation and Chat with Home
document.addEventListener('DOMContentLoaded', function () {
    // Handle chat input on HOME page
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');

    function sendChatMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // Add user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'chat-message user';
            userMessageDiv.innerHTML = `<div class="message-bubble">${message}</div>`;
            chatMessages.appendChild(userMessageDiv);

            // Clear input
            chatInput.value = '';

            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Simulate assistant response (in production, this will call an API)
            setTimeout(() => {
                const assistantMessageDiv = document.createElement('div');
                assistantMessageDiv.className = 'chat-message assistant';
                assistantMessageDiv.innerHTML = `<div class="message-bubble">Obrigada pela sua mensagem! Em breve isso será conectado à API. 🌟</div>`;
                chatMessages.appendChild(assistantMessageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 1000);
        }
    }

    if (chatSendBtn && chatInput) {
        chatSendBtn.addEventListener('click', sendChatMessage);

        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }

    // ========= MAPA ASTRAL COM CHAT =========

    // Variáveis globais para o chat
    let mapaData = null;
    let chatHistory = [];
    const API_BASE_URL = 'https://api-mapa-astral-production.up.railway.app';

    const mapaForm = document.getElementById('mapa-astral-form');
    if (mapaForm) {
        mapaForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Pegar os dados do formulário
            const nome = document.getElementById('nome').value;
            const dataNascimento = document.getElementById('data-nascimento').value;
            const horaNascimento = document.getElementById('hora-nascimento').value;
            const localNascimento = document.getElementById('local-nascimento').value;

            // Separar local em cidade e país
            const localParts = localNascimento.split(',').map(p => p.trim());
            const cidade = localParts[0] || localNascimento;
            const pais = localParts[localParts.length - 1] || 'Brasil';

            // Esconder formulário e mostrar chat
            document.getElementById('form-card').style.display = 'none';
            document.getElementById('chat-card').style.display = 'block';
            document.getElementById('chat-loading').style.display = 'flex';
            document.getElementById('chat-interface').style.display = 'none';

            try {
                // 1. Calcular mapa astral
                const payload = {
                    date: dataNascimento,
                    time: horaNascimento,
                    city: cidade,
                    country: pais
                };

                const response = await fetch(`${API_BASE_URL}/calculate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Erro ao calcular mapa astral');
                }

                mapaData = await response.json();
                console.log('Mapa calculado:', mapaData);

                // 2. Mostrar interface de chat
                document.getElementById('chat-loading').style.display = 'none';
                document.getElementById('chat-interface').style.display = 'block';

                // 3. Enviar mensagem inicial automática
                await sendInitialMessage(nome);

            } catch (error) {
                console.error('Erro:', error);
                document.getElementById('chat-loading').innerHTML = `
                    <p style="color: #ff6b6b;">${error.message}</p>
                    <button class="btn-secondary" onclick="location.reload()">Tentar Novamente</button>
                `;
            }
        });
    }

    // Função para enviar mensagem inicial
    async function sendInitialMessage(nome) {
        const initialMessage = `Olá! Meu mapa astral foi calculado. Me ajude a entendê-lo.`;

        // Adicionar mensagem do usuário
        addMessageToChat('user', initialMessage);

        // Chamar a IA
        await sendMessageToAI(initialMessage);
    }

    // Função para adicionar mensagem ao chat
    function addMessageToChat(role, content) {
        const messagesContainer = document.getElementById('chat-messages-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-msg ${role}`;

        if (role === 'assistant') {
            messageDiv.innerHTML = `
                <div class="msg-avatar">🤖</div>
                <div class="msg-content">${formatMarkdown(content)}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="msg-content">${escapeHtml(content)}</div>
                <div class="msg-avatar">👤</div>
            `;
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Adicionar ao histórico
        chatHistory.push({ role, content });
    }

    // Função para enviar mensagem para a IA
    async function sendMessageToAI(message) {
        try {
            const payload = {
                message: message,
                map_data: mapaData,
                history: chatHistory.slice(0, -1) // Não incluir a mensagem atual
            };

            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error('Erro ao conectar com a IA');
            }

            const data = await response.json();
            addMessageToChat('assistant', data.response);

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            addMessageToChat('assistant', 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.');
        }
    }

    // Event listener para enviar mensagens
    const chatSendBtnMapa = document.getElementById('chat-send-btn');
    const chatInputMapa = document.getElementById('chat-message-input');

    if (chatSendBtnMapa && chatInputMapa) {
        chatSendBtnMapa.addEventListener('click', () => sendChatMessageMapa());
        chatInputMapa.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessageMapa();
        });
    }

    function sendChatMessageMapa() {
        const message = chatInputMapa.value.trim();
        if (!message) return;

        // Adicionar mensagem do usuário
        addMessageToChat('user', message);

        // Limpar input
        chatInputMapa.value = '';

        // Enviar para IA
        sendMessageToAI(message);
    }

    // Botão Nova Consulta
    const btnNewChart = document.getElementById('btn-new-chart');
    if (btnNewChart) {
        btnNewChart.addEventListener('click', function () {
            // Reset tudo
            mapaData = null;
            chatHistory = [];
            document.getElementById('chat-messages-container').innerHTML = '';
            document.getElementById('chat-card').style.display = 'none';
            document.getElementById('form-card').style.display = 'block';
            document.getElementById('mapa-astral-form').reset();
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
        // Formatação básica de markdown
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
});
