// --- UTILS FUNCTIONS ---

/**
 * 
 * Transform a timestamp in ISO format to a human-readable format.
 * 
 * @param timestampISO - The timestamp of a message in ISO format.
 * @returns Timestamp formatted in the user's locale or default to 'es-ES'.
 */
function formatTimestamp(timestampISO) {

    if (!timestampISO) return ''

    try {

        const date = new Date(timestampISO)

        const options = {
            day: 'numeric',
            month: 'short',
            hour: 'numeric',
            minute: '2-digit',
            hour12: false,
        }

        return new Intl.DateTimeFormat(navigator.language || 'es-ES', options).format(date)

    } catch (e) {
        console.error('Error formatting timestamp:', e)
        return ''
    }

}

/**
 * Loop through all message timestamps in the chat window and formats them.
 * @param chatWindow - DOMElement representing the chat window. 
 */
function formatTimestampsOnChatWindow(chatWindow) {
    const timestampElements = chatWindow.querySelectorAll('.message-timestamp[data-timestamp]')

    timestampElements.forEach(element => {
        const timestampISO = element.dataset.timestamp
        element.textContent = formatTimestamp(timestampISO)
    })
}

/**
 * Scrolls the chat window to the bottom.
 * @param chatWindow - DOMElement representing the chat window. 
 */
function scrollToBottom(chatWindow) {
    setTimeout(() => {
        chatWindow.scrollTop = chatWindow.scrollHeight
    }, 50)
}

// Function to show typing indicator
function showTypingIndicator(typingIndicator, chatWindow) {
    typingIndicator.classList.remove('d-none')
    typingIndicator.classList.add('d-flex')
    scrollToBottom(chatWindow)
}

// Function to hide typing indicator
function hideTypingIndicator(typingIndicator) {
    typingIndicator.classList.add('d-none')
    typingIndicator.classList.remove('d-flex')
}

document.addEventListener('DOMContentLoaded', function () {

    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const csrfToken = document.getElementById('csrf_token').value;

    // --- MESSAGES FUNCTIONS ---

    // Function to add a message to the chat window
    function addMessage(text, isUser = false, isoTimestamp = null) {

        // Create message container
        const messageContainer = document.createElement('div')
        messageContainer.classList.add('d-flex', 'mb-3')
        messageContainer.classList.add(isUser ? 'justify-content-end' : 'justify-content-start')

        // Create icon element
        let iconElement = document.createElement('img')
        iconElement.classList.add('rounded-circle', 'me-2', 'align-self-end')
        if (isUser) {
            iconElement.src = USER_ICON_URL
            iconElement.alt = "User-Icon-Message"
        } else {
            iconElement.src = BOT_ICON_URL
            iconElement.alt = "Bot-Icon-Message"
        }

        // Create message div
        const messageDiv = document.createElement('div')
        messageDiv.classList.add('p-2', 'px-3', 'rounded', 'mw-75')
        if (isUser)
            messageDiv.classList.add('bg-primary', 'text-white')
        else
            messageDiv.classList.add('bg-white', 'border')

        // Sanitize text and add message text
        const sanitizedText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;")
        const messageText = document.createElement('div')
        messageText.classList.add('message-text')
        messageText.innerHTML = sanitizedText.replace(/\n/g, '<br>')
        messageDiv.appendChild(messageText)

        // Create timestamp
        const timestampSmall = document.createElement('small')
        timestampSmall.classList.add('message-timestamp', 'd-block', 'mt-1')
        if (isUser) {
            timestampSmall.classList.add('text-white-50')
            timestampSmall.classList.remove('text-end')
        } else {
            timestampSmall.classList.add('text-muted')
            timestampSmall.classList.remove('text-start')
        }
        const timestampToFormat = isoTimestamp || new Date().toISOString()
        timestampSmall.textContent = formatTimestamp(timestampToFormat)
        messageDiv.appendChild(timestampSmall)

        // Final message container and elements
        if (!isUser) {
            messageContainer.appendChild(iconElement)
            messageContainer.appendChild(messageDiv)
        } else {
            messageContainer.appendChild(messageDiv)
            messageContainer.appendChild(iconElement)
        }

        // Insert the row before typing indicator
        chatWindow.insertBefore(messageContainer, typingIndicator);
        scrollToBottom(chatWindow);

        return messageContainer;
    }

    // Function to send message to server and get response
    async function sendMessage(text) {

        addMessage(text, true) // Add user message to UI
        userInput.value = '' // Clear input field

        try {
            showTypingIndicator(typingIndicator, chatWindow)

            // Send message to server
            const response = await fetch(CHAT_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ message: text }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error. Status: ${response.status}`)
            }

            const data = await response.json()
            hideTypingIndicator(typingIndicator)

            addMessage(data.response, false, data.timestamp)

        } catch (error) {

            hideTypingIndicator(typingIndicator)
            console.error('Error sending/receiving message:', error)

            // Add error message to UI
            addMessage("Sorry, I encountered an error. Please try again.", false)
        }
    }

    // --- SEND MESSAGE HANDLER ---

    // Whenever user clicks the SEND button, sends the message.
    sendBtn.addEventListener('click', function () {
        const text = userInput.value.trim();
        if (text)
            sendMessage(text);
    })

    // Whenever user presses ENTER, sends the message.
    userInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()

            const text = userInput.value.trim();
            if (text)
                sendMessage(text);
        }
    })

    // --- SETUP ---

    formatTimestampsOnChatWindow(chatWindow) // For initial messages
    scrollToBottom(chatWindow) // Scroll to bottom on load
    hideTypingIndicator(typingIndicator) // Hide typing indicator on load

});