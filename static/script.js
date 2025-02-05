document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    const userInput = document.getElementById("user-input").value.trim();
    if (!userInput) return;

    // Ajouter le message de l'utilisateur à la boîte de discussion
    appendMessage("user", userInput);

    // Envoyer la question au serveur
    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userInput }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.message) {
            appendMessage("bot", data.message);
        } else if (data.error) {
            appendMessage("bot", "Error: " + data.error);
        }
    })
    .catch((error) => {
        appendMessage("bot", "Error: " + error.message);
    });

    // Effacer le champ de saisie
    document.getElementById("user-input").value = "";
}

function appendMessage(sender, message) {
    const chatBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", `${sender}-message`);
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);

    // Faire défiler vers le bas pour voir le dernier message
    chatBox.scrollTop = chatBox.scrollHeight;
}