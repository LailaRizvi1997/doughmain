async function sendMessage() {
    const userInput = document.getElementById("user-input").value.trim();
    if (!userInput) return;

    const chatBox = document.getElementById("chat-box");

    // Add user's message to the chat
    const userMessage = document.createElement("div");
    userMessage.classList.add("message", "user-message");
    userMessage.innerText = userInput;
    chatBox.appendChild(userMessage);

    // Clear the input field
    document.getElementById("user-input").value = "";

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("/ask_bot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput }),
        });

        const result = await response.json();

        // Add bot's reply to the chat
        if (result.reply) {
            const botMessage = document.createElement("div");
            botMessage.classList.add("message", "bot-message");
            botMessage.innerText = result.reply;
            chatBox.appendChild(botMessage);
        } else {
            throw new Error("No reply received from bot.");
        }
    } catch (error) {
        console.error("Error:", error);

        // Show an error message in the chat
        const errorMessage = document.createElement("div");
        errorMessage.classList.add("message", "error-message");
        errorMessage.innerText = "Error: Unable to connect to Doughbot.";
        chatBox.appendChild(errorMessage);
    }

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}
