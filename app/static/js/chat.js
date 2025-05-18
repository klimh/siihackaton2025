document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const messagesArea = document.getElementById('messagesArea');
    const averageMood = document.getElementById('averageMood');
    const moodDeviation = document.getElementById('moodDeviation');
    const currentSentiment = document.getElementById('currentSentiment');

    // Get CSRF token with error handling
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (!csrfToken) {
        appendErrorMessage('CSRF token not found. Please refresh the page.');
        return;
    }
    const token = csrfToken.getAttribute('content');
    if (!token) {
        appendErrorMessage('Invalid CSRF token. Please refresh the page.');
        return;
    }

    // Load initial chat history and mood analysis
    loadChatHistory();
    updateMoodAnalysis();

    // Handle form submission
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;

        // Disable form while sending
        const submitButton = chatForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': token
                },
                body: JSON.stringify({ message })
            });

            // Clear input
            messageInput.value = '';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error: ${response.status} - ${response.statusText}`);
            }

            const data = await response.json();
            
            // Add messages to chat
            appendMessage(message, 'user');
            appendMessage(data.message, 'ai');

            // Update mood analysis
            updateMoodAnalysis();

            // Scroll to bottom
            scrollToBottom();

        } catch (error) {
            console.error('Error:', error);
            appendErrorMessage(error.message || 'Failed to send message. Please try again.');
        } finally {
            // Re-enable form
            submitButton.disabled = false;
            submitButton.textContent = 'Send';
        }
    });

    async function loadChatHistory() {
        try {
            const response = await fetch('/api/chat/history', {
                headers: {
                    'X-CSRF-TOKEN': token
                }
            });
            if (!response.ok) {
                throw new Error('Failed to load chat history');
            }

            const data = await response.json();
            
            // Clear loading message
            messagesArea.innerHTML = '';

            // Display messages
            data.forEach(msg => {
                appendMessage(msg.message, msg.sender, false);
            });

            scrollToBottom();

        } catch (error) {
            console.error('Error:', error);
            appendErrorMessage('Failed to load chat history');
        }
    }

    async function updateMoodAnalysis() {
        try {
            const response = await fetch('/api/mood_analysis', {
                headers: {
                    'X-CSRF-TOKEN': token
                }
            });
            if (!response.ok) {
                throw new Error('Failed to load mood analysis');
            }

            const data = await response.json();
            
            // Update mood statistics
            averageMood.textContent = data.average_mood.toFixed(1) + '/10';
            moodDeviation.textContent = data.mood_deviation.toFixed(1);
            
            // Update sentiment if available
            if (data.current_sentiment !== undefined) {
                const sentimentText = getSentimentText(data.current_sentiment);
                currentSentiment.textContent = sentimentText;
            }

        } catch (error) {
            console.error('Error:', error);
            averageMood.textContent = '-';
            moodDeviation.textContent = '-';
            currentSentiment.textContent = '-';
        }
    }

    function appendMessage(message, sender, shouldScroll = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`;

        const bubble = document.createElement('div');
        bubble.className = sender === 'user' 
            ? 'bg-blue-600 text-white rounded-lg py-2 px-4 max-w-[70%]'
            : 'bg-gray-200 text-gray-800 rounded-lg py-2 px-4 max-w-[70%]';
        bubble.textContent = message;

        messageDiv.appendChild(bubble);
        messagesArea.appendChild(messageDiv);

        if (shouldScroll) {
            scrollToBottom();
        }
    }

    function appendErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-center text-red-500 my-2';
        errorDiv.textContent = message;
        messagesArea.appendChild(errorDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    function getSentimentText(score) {
        if (score >= 0.5) return 'Very Positive';
        if (score >= 0.1) return 'Positive';
        if (score > -0.1) return 'Neutral';
        if (score > -0.5) return 'Negative';
        return 'Very Negative';
    }
}); 