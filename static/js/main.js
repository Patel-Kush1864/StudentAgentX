document.addEventListener("DOMContentLoaded", function () {
    // Mobile Sidebar toggle control
    const toggleBtn = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");

    if (toggleBtn && sidebar && overlay) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("show");
            overlay.classList.toggle("show");
        });

        overlay.addEventListener("click", function () {
            sidebar.classList.remove("show");
            overlay.classList.remove("show");
        });

        // Close sidebar on link click (useful in mobile single-page or transition views)
        const links = sidebar.querySelectorAll(".sidebar-link");
        links.forEach(link => {
            link.addEventListener("click", function () {
                sidebar.classList.remove("show");
                overlay.classList.remove("show");
            });
        });
    }

    // Chat client interface
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");

    if (chatForm && chatInput && chatMessages) {
        chatForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            // Render user message bubble
            appendMessage("user", message);
            chatInput.value = "";

            // Show typing indicator
            const typingIndicator = appendTypingIndicator();

            // Request AI prediction via REST API
            fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                typingIndicator.remove();
                if (data.status === "success") {
                    appendMessage("ai", data.reply);
                } else {
                    appendMessage("ai", "[ERROR] AI Agent failed: " + data.message);
                }
            })
            .catch(error => {
                typingIndicator.remove();
                appendMessage("ai", "[ERROR] Connection lost: " + error.message);
            });
        });
    }

    function appendMessage(sender, text) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble chat-bubble-${sender}`;
        
        // Convert basic markdown tags to simple HTML
        let formattedText = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");
            
        bubble.innerHTML = formattedText;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const container = document.createElement("div");
        container.className = "chat-bubble chat-bubble-ai d-flex align-items-center gap-2";
        container.innerHTML = `
            <span>Autonomous Master Agent is thinking...</span>
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        chatMessages.appendChild(container);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return container;
    }
});
