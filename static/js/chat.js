document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatForm) return;

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';

        // Add typing indicator
        const loadingId = addTypingIndicator();

        // Send to API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                removeMessage(loadingId);
                if (data.error) {
                    addMessage('Lo siento, hubo un error al procesar tu solicitud.', 'ai');
                } else {
                    addMessage(data.answer, 'ai', data.sources);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                removeMessage(loadingId);
                addMessage('Lo siento, hubo un error de conexión.', 'ai');
            });
    });

    function addMessage(text, sender, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        let contentHtml = text.replace(/\n/g, '<br>');

        if (sources && sources.length > 0) {
            contentHtml += '<div class="sources-list"><strong>Fuentes:</strong><br>';
            sources.forEach(source => {
                const date = source.published ? new Date(source.published).toLocaleDateString() : '';
                contentHtml += `<a href="${source.url}" target="_blank" class="source-item">
                    ▶ ${source.title} ${date ? `(${date})` : ''}
                </a>`;
            });
            contentHtml += '</div>';
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                ${contentHtml}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv.id;
    }

    function addTypingIndicator() {
        const id = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.id = id;
        messageDiv.classList.add('message', 'ai-message');
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const element = document.getElementById(id);
        if (element) {
            element.remove();
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
