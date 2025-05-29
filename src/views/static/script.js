// Select DOM elements
const chatbotToggler = document.querySelector(".toggle-chat");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".message-box");
const chatInput = document.querySelector(".message-input textarea");
const sendChatBtn = document.querySelector("#send-btn");

// Initialize variables
let userMessage = null; // To store the user message
let isSending = false;  // To prevent multiple sends
const inputInitHeight = chatInput.scrollHeight; // Store initial textarea height

// Function to convert URLs in message text to clickable links
function linkifyText(text) {
    const urlPattern = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|$!:,.;]*[-A-Z0-9+&@#\/%?=~_|$])/ig;
    return text.replace(urlPattern, (url) => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });
}

// Function to replace asterisks with <strong> tags for bold text
function formatBoldText(text) {
    return text.replace(/\*(.*?)\*/g, '<strong>$1</strong>'); // Replace *text* with <strong>text</strong>
}

// Function to sanitize HTML
function sanitizeHTML(text) {
    const tempDiv = document.createElement('div');
    tempDiv.textContent = text;
    return tempDiv.innerHTML;
}

// Function to process the message text (links and bold formatting)
function processMessageText(text) {
    text = linkifyText(text); // Convert URLs to clickable links
    text = formatBoldText(text); // Convert *text* to <strong>text</strong>
    return sanitizeHTML(text); // Sanitize HTML to prevent XSS
}

// Creates a new chat <li> element with the given message and className
const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("message", className); // Apply message class

    // Set content based on the message type (outgoing/incoming)
    const chatContent = className === "outgoing" ? `<p></p>` : `<img src="/static/images/rvistlogo.jpg" alt="RVIST" class="chat-icon"><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").innerHTML = processMessageText(message); // Set the message text with processed text

    return chatLi; // Return the created chat <li> element
}

// Creates a typing indicator <li> element
const createTypingIndicator = () => {
    const typingLi = document.createElement("li");
    typingLi.classList.add("message", "incoming", "typing-indicator");
    typingLi.innerHTML = `
        <img src="/static/images/rvistlogo.jpg" alt="RVIST" class="chat-icon">
        <div class="typing">
            <span></span><span></span><span></span>
        </div>
    `;
    return typingLi;
}

// Generates a response using the Flask API and updates the chat element
const generateResponse = async (message) => {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message: message }),
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        return data.response || 'I’m not sure how to respond to that right now. Could you ask something else?';
    } catch (error) {
        console.error('Error:', error);
        // Return a friendly fallback response instead of a technical error message
        return 'I’m not sure how to respond to that right now. Could you ask something else?';
    }
}

// Handle sending the message
const handleSendMessage = async () => {
    if (isSending || !chatInput.value.trim()) return; // Avoid duplicate sends
    isSending = true; // Set flag to prevent duplicate sends

    // Disable input and send button to prevent multiple sends
    chatInput.disabled = true;
    sendChatBtn.style.pointerEvents = 'none';

    userMessage = chatInput.value.trim(); // Get the user message and remove extra spaces

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, 'outgoing'));
    chatInput.value = ''; // Clear the input field

    // Append typing indicator
    const typingIndicator = createTypingIndicator();
    chatbox.appendChild(typingIndicator);
    scrollToBottom(); // Scroll chatbox to bottom

    // Send the user's message to the server and get the response
    const responseMessage = await generateResponse(userMessage);

    // Remove typing indicator after a short delay
    setTimeout(() => {
        typingIndicator.remove();

        // Append the response message to the chatbox
        chatbox.appendChild(createChatLi(responseMessage, 'incoming'));
        scrollToBottom(); // Scroll chatbox to bottom

        // Enable input and send button
        chatInput.disabled = false;
        sendChatBtn.style.pointerEvents = 'auto';

        isSending = false; // Reset flag
    }, 1000); // Delay to simulate typing effect
}

// Auto-scroll function for the chatbox
const scrollToBottom = () => {
    setTimeout(() => {
        chatbox.scrollTop = chatbox.scrollHeight;
    }, 100); // Slight delay for smooth scrolling
}



// Toggle chat interface visibility
const toggleChat = () => {
    document.body.classList.toggle('show-chatbot');
    if (document.body.classList.contains('show-chatbot')) {
        chatInput.focus(); // Focus input field when chat opens
    }
}

// Event listeners
sendChatBtn.addEventListener('click', handleSendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Prevent the default form submission
        handleSendMessage();
    }
});
chatbotToggler.addEventListener('click', toggleChat);
closeBtn.addEventListener('click', toggleChat);

// Resize input field based on content
chatInput.addEventListener('input', () => {
    chatInput.style.height = inputInitHeight + "px"; // Reset height
    chatInput.style.height = chatInput.scrollHeight + "px"; // Set new height

    // Enable or disable send button based on input
    sendChatBtn.style.visibility = chatInput.value.trim() ? 'visible' : 'hidden';
});
