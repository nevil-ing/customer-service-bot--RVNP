// ------------  Element handles ------------
const chatbotToggler = document.querySelector(".toggle-chat");
const closeBtn       = document.querySelector(".close-btn");
const chatbox        = document.querySelector(".message-box");
const chatInput      = document.querySelector(".message-input textarea");
const sendChatBtn    = document.querySelector("#send-btn");

// ------------  State ------------
let isSending       = false;
const inputInitH    = chatInput.scrollHeight;

// ------------  Text helpers ------------
const urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|$!:,.;]*[-A-Z0-9+&@#\/%?=~_|$])/ig;

// Sanitise FIRST, then format
const sanitize = (str) => {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
};
const linkify  = (str) => str.replace(urlRegex, (url) =>
    `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
);
const boldify  = (str) => str.replace(/\*(.*?)\*/g, "<strong>$1</strong>");

const processText = (raw) => boldify(linkify(sanitize(raw)));

// ------------  DOM builders ------------
const mkMessageLi = (text, outgoing = false) => {
    const li = document.createElement("li");
    li.classList.add("message", outgoing ? "outgoing" : "incoming");

    if (!outgoing) {
        li.innerHTML = `<img src="/static/images/rvistlogo.jpg" alt="RVIST" class="chat-icon"><p></p>`;
    } else {
        li.innerHTML = `<p></p>`;
    }
    li.querySelector("p").innerHTML = processText(text);
    return li;
};

const mkTypingLi = () => {
    const li = document.createElement("li");
    li.classList.add("message", "incoming", "typing-indicator");
    li.innerHTML = `
        <img src="/static/images/rvistlogo.jpg" alt="RVIST" class="chat-icon">
        <div class="typing"><span></span><span></span><span></span></div>
    `;
    return li;
};

// ------------  Networking ------------
async function fetchBotReply(message) {
    const res = await fetch("/chat", {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ message })
    });
    if (!res.ok) throw new Error(`Server ${res.status}`);
    const data = await res.json();
    return data.response || "I’m not sure how to respond to that right now. Could you ask something else?";
}

// ------------  UI actions ------------
async function sendMessage() {
    const raw = chatInput.value.trim();
    if (isSending || !raw) return;

    isSending       = true;
    chatInput.value = "";
    chatInput.style.height = `${inputInitH}px`;
    chatInput.disabled     = true;
    sendChatBtn.style.pointerEvents = "none";

    chatbox.appendChild(mkMessageLi(raw, true));
    const typingLi = mkTypingLi();
    chatbox.appendChild(typingLi);
    scrollBottom();

    let reply;
    try   { reply = await fetchBotReply(raw); }
    catch (e) {
        console.error(e);
        reply = "⚠️ Server error. Please try again later.";
    }

    // Maintain illusion of typing for at least 800 ms
    setTimeout(() => {
        typingLi.remove();
        chatbox.appendChild(mkMessageLi(reply));
        scrollBottom();

        isSending                        = false;
        chatInput.disabled               = false;
        sendChatBtn.style.pointerEvents  = "auto";
        sendChatBtn.style.visibility     = "hidden";
        chatInput.focus();
    }, 800);
}

function scrollBottom() {
    setTimeout(() => chatbox.scrollTop = chatbox.scrollHeight, 100);
}

// ------------  Chat visibility ------------
function toggleChat() {
    document.body.classList.toggle("show-chatbot");
    if (document.body.classList.contains("show-chatbot")) chatInput.focus();
}

// ------------  Event hooks ------------
sendChatBtn.addEventListener("click", sendMessage);

chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

chatInput.addEventListener("input", () => {
    chatInput.style.height = `${inputInitH}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
    sendChatBtn.style.visibility = chatInput.value.trim() ? "visible" : "hidden";
});

chatbotToggler.addEventListener("click", toggleChat);
closeBtn.addEventListener("click", toggleChat);
