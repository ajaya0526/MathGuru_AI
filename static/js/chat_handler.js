// =========================
// Chat Handler for MathGuruAI Chat Page
// =========================

async function sendMessage() {
    const chatInput = document.getElementById("chatInput");
    const chatBox = document.getElementById("chatBox");

    const userMessage = chatInput.value.trim();

    if (!userMessage) {
        alert("❗ Please type a question to ask!");
        return;
    }

    // Display user message
    const userBubble = document.createElement('div');
    userBubble.className = 'message user-message';
    userBubble.innerHTML = `<b>You:</b> ${escapeHtml(userMessage)}`;
    chatBox.appendChild(userBubble);

    chatInput.value = ''; // Clear input
    chatInput.disabled = true;

    // Auto scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // ✅ FIXED: Correct endpoint for chat
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();

        // Display bot reply
        const botBubble = document.createElement('div');
        botBubble.className = 'message bot-message';
        botBubble.innerHTML = `<b>MathGuru:</b> ${escapeHtml(data.reply || '🤖 Sorry, I could not generate a response.')}`;
        chatBox.appendChild(botBubble);

    } catch (err) {
        console.error("[Chat Handler Error]:", err);

        const errorBubble = document.createElement('div');
        errorBubble.className = 'message bot-message';
        errorBubble.innerHTML = `<b>MathGuru:</b> ⚠️ Sorry, I could not connect. Please try again later.`;
        chatBox.appendChild(errorBubble);
    } finally {
        chatInput.disabled = false;
        chatInput.focus();
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Optional: Send message on Enter key press
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById("chatInput");
    chatInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});

// Escape HTML to prevent XSS
function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function (match) {
        const escapeChars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return escapeChars[match];
    });
}
