// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const micBtn = document.getElementById('micBtn');
const voiceToggleBtn = document.getElementById('voiceToggleBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorToast = document.getElementById('errorToast');
const errorMessage = document.getElementById('errorMessage');
const charCount = document.getElementById('charCount');

// State
let isTyping = false;
let isRecording = false;
let voiceEnabled = true;
let recognition = null;
let synthesis = window.speechSynthesis;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    adjustTextareaHeight();
    loadChatHistory();
    initializeSpeechRecognition();
    updateVoiceButton();
});

// Event Listeners
function setupEventListeners() {
    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);
    
    // Send message on Enter (new line on Shift+Enter)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Clear chat
    clearChatBtn.addEventListener('click', clearChat);
    
    // Voice toggle
    voiceToggleBtn.addEventListener('click', toggleVoice);
    
    // Microphone button
    micBtn.addEventListener('click', toggleRecording);
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        adjustTextareaHeight();
        updateCharCount();
        toggleSendButton();
    });
    
    // Focus input on load
    messageInput.focus();
}

// Adjust textarea height based on content
function adjustTextareaHeight() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

// Update character count
function updateCharCount() {
    const length = messageInput.value.length;
    charCount.textContent = `${length} / 2000`;
    
    if (length > 1800) {
        charCount.style.color = '#ef4444';
    } else if (length > 1500) {
        charCount.style.color = '#f59e0b';
    } else {
        charCount.style.color = '#64748b';
    }
}

// Toggle send button based on input
function toggleSendButton() {
    const hasText = messageInput.value.trim().length > 0;
    sendBtn.disabled = !hasText || isTyping;
}

// Send message function
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isTyping) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    adjustTextareaHeight();
    updateCharCount();
    toggleSendButton();
    
    // Show loading
    showLoading();
    isTyping = true;
    
    try {
        // Send to backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get response');
        }
        
        // Add bot response
        addMessage(data.response, 'bot');
        
        // Save to history
        saveChatHistory();
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to send message. Please try again.');
    } finally {
        hideLoading();
        isTyping = false;
        toggleSendButton();
        messageInput.focus();
    }
}

// Add message to chat
function addMessage(content, sender) {
    // Remove welcome message if it exists
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Process message content for links and formatting
    messageContent.innerHTML = formatMessage(content);
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = getCurrentTime();
    
    messageContent.appendChild(messageTime);
    
    if (sender === 'user') {
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(avatar);
    } else {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

// Format message content (links, line breaks)
function formatMessage(content) {
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Convert line breaks to <br>
    content = content.replace(/\n/g, '<br>');
    
    return content;
}

// Get current time string
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show loading overlay
function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorToast.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Hide error message
function hideError() {
    errorToast.classList.add('hidden');
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the entire chat history?')) {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <i class="fas fa-robot welcome-icon"></i>
                <h2>Welcome to AI Assistant</h2>
                <p>I'm here to help you with any questions you have. Just type your message below and press Enter!</p>
            </div>
        `;
        
        // Clear localStorage
        localStorage.removeItem('chatHistory');
        
        // Focus input
        messageInput.focus();
    }
}

// Save chat history to localStorage
function saveChatHistory() {
    const messages = [];
    const messageElements = document.querySelectorAll('.message');
    
    messageElements.forEach(element => {
        const content = element.querySelector('.message-content').cloneNode(true);
        const timeElement = content.querySelector('.message-time');
        if (timeElement) {
            timeElement.remove();
        }
        
        messages.push({
            sender: element.classList.contains('user') ? 'user' : 'bot',
            content: content.innerHTML,
            timestamp: new Date().toISOString()
        });
    });
    
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

// Load chat history from localStorage
function loadChatHistory() {
    const savedHistory = localStorage.getItem('chatHistory');
    
    if (savedHistory) {
        try {
            const messages = JSON.parse(savedHistory);
            
            // Remove welcome message
            const welcomeMessage = document.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
            
            // Restore messages
            messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.sender}`;
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.innerHTML = msg.sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
                
                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                messageContent.innerHTML = msg.content;
                
                const messageTime = document.createElement('div');
                messageTime.className = 'message-time';
                messageTime.textContent = new Date(msg.timestamp).toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    hour12: true 
                });
                
                messageContent.appendChild(messageTime);
                
                if (msg.sender === 'user') {
                    messageDiv.appendChild(messageContent);
                    messageDiv.appendChild(avatar);
                } else {
                    messageDiv.appendChild(avatar);
                    messageDiv.appendChild(messageContent);
                }
                
                chatMessages.appendChild(messageDiv);
            });
            
            scrollToBottom();
            
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        clearChat();
    }
    
    // Escape to focus input
    if (e.key === 'Escape') {
        messageInput.focus();
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    scrollToBottom();
});

// Prevent accidental page leave during typing
window.addEventListener('beforeunload', (e) => {
    if (messageInput.value.trim().length > 0) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Voice Functions
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add('recording');
            micBtn.innerHTML = '<i class="fas fa-stop"></i>';
        };

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            
            // Update input in real-time for user feedback
            messageInput.value = transcript;
            adjustTextareaHeight();
            updateCharCount();
            toggleSendButton();
            
            // Auto-send when speech is complete
            if (event.results[event.results.length - 1].isFinal) {
                stopRecording();
                // Auto-send after a short delay for better UX
                setTimeout(() => {
                    if (messageInput.value.trim()) {
                        sendMessage();
                    }
                }, 500);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            let errorMessage = 'Speech recognition error: ' + event.error;
            
            // Provide specific help for common errors
            if (event.error === 'not-allowed') {
                errorMessage = 'Microphone access denied. Please allow microphone access in your browser settings and refresh the page.';
            } else if (event.error === 'no-speech') {
                errorMessage = 'No speech detected. Please try speaking clearly.';
            } else if (event.error === 'network') {
                errorMessage = 'Network error. Please check your internet connection.';
            } else if (event.error === 'service-not-allowed') {
                errorMessage = 'Speech recognition service not allowed. Please check your browser settings.';
            }
            
            showError(errorMessage);
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };
    } else {
        micBtn.style.display = 'none';
        voiceToggleBtn.style.display = 'none';
        console.warn('Speech recognition not supported');
    }
}

function toggleRecording() {
    if (!recognition) {
        showError('Speech recognition is not supported in your browser');
        return;
    }

    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    if (recognition && !isRecording) {
        // Request microphone permission first
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                // Stop the stream immediately (we just need permission)
                stream.getTracks().forEach(track => track.stop());
                // Start speech recognition
                recognition.start();
            })
            .catch(err => {
                console.error('Microphone permission denied:', err);
                showError('Microphone access denied. Please allow microphone access in your browser settings and refresh the page.');
            });
    }
}

function stopRecording() {
    if (recognition && isRecording) {
        recognition.stop();
    }
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
}

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    updateVoiceButton();
    
    if (!voiceEnabled) {
        synthesis.cancel(); // Stop any ongoing speech
    }
}

function updateVoiceButton() {
    if (voiceEnabled) {
        voiceToggleBtn.classList.add('active');
        voiceToggleBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
        voiceToggleBtn.title = 'Voice Enabled';
    } else {
        voiceToggleBtn.classList.remove('active');
        voiceToggleBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
        voiceToggleBtn.title = 'Voice Disabled';
    }
}

function speakText(text) {
    if (!voiceEnabled || !synthesis) {
        return;
    }

    // Cancel any ongoing speech
    synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Get available voices and select a good one
    const voices = synthesis.getVoices();
    if (voices.length > 0) {
        // Prefer female voices for assistant
        const femaleVoice = voices.find(voice => 
            voice.name.includes('Female') || 
            voice.name.includes('Samantha') || 
            voice.name.includes('Karen') ||
            voice.name.includes('Moira')
        );
        utterance.voice = femaleVoice || voices[0];
    }

    synthesis.speak(utterance);
}

// Modify the addMessage function to include speech
const originalAddMessage = addMessage;
addMessage = function(content, sender) {
    originalAddMessage(content, sender);
    
    // Speak bot responses if voice is enabled
    if (sender === 'bot' && voiceEnabled) {
        // Clean the text by removing HTML tags
        const cleanText = content.replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
        speakText(cleanText);
    }
};

// Load voices when they become available
if (synthesis) {
    synthesis.onvoiceschanged = () => {
        synthesis.getVoices();
    };
}
