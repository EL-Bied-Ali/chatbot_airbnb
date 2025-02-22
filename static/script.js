let threadId = "123456789";  // Example thread ID
let lastEdit = "";  // Store last edit for undo functionality
let airbnbLink = "";  // Store Airbnb thread link

// Load the conversation and extract the Airbnb link
function loadConversation() {
    fetch(`/conversation?thread=${threadId}`)
        .then(response => response.json())
        .then(data => {
            let historyDiv = document.getElementById("conversation-history");
            let lastMessage = data.length > 0 ? data[data.length - 1] : null;

            if (lastMessage) {
                historyDiv.innerHTML = data.map(msg =>
                    `<p><b>${msg.sender} (${msg.role}):</b> ${msg.message} 
                    <small>${new Date(msg.timestamp).toLocaleString()}</small></p>`).join('');

                let aiResponseBox = document.getElementById("ai-response-box");
                lastEdit = aiResponseBox.value = lastMessage.message; // Store last message for undo
                
                // ✅ Retrieve Airbnb link from backend when saving
                airbnbLink = lastMessage.airbnb_link || "";
            } else {
                historyDiv.innerHTML = "<p>No messages yet.</p>";
                document.getElementById("ai-response-box").value = ""; // Clear AI response box if empty
            }
        })
        .catch(error => console.error("Error loading conversation:", error));
}

// ✅ Save the edited AI response and redirect to Airbnb
function saveEditedResponse() {
    let aiResponseBox = document.getElementById("ai-response-box");
    let editedMessage = aiResponseBox.value.trim();

    if (!editedMessage) {
        alert("AI response cannot be empty!");
        return;
    }

    fetch(`/conversation/edit_response/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: threadId, message: editedMessage })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "Response edited") {
            lastEdit = editedMessage; // Store last edit for undo
            copyToClipboard(editedMessage); // ✅ Copy response to clipboard

            // ✅ Remove alert and directly redirect
            if (data.airbnb_link) {
                let encodedResponse = encodeURIComponent(editedMessage);
                let redirectUrl = `/prefill_message?response=${encodedResponse}&thread=${encodeURIComponent(data.airbnb_link)}`;
                window.location.href = redirectUrl; // ✅ Instantly redirect
            }
        } else {
            alert("Error saving response: " + data.error);
        }
    })
    .catch(error => console.error("Error saving response:", error));
}



// Undo last edit
function undoEdit() {
    let aiResponseBox = document.getElementById("ai-response-box");
    aiResponseBox.value = lastEdit; // Restore previous version
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => console.log("Copied to clipboard:", text))
        .catch(err => console.error("Failed to copy:", err));
}

// Send extra apartment details
function sendApartmentInfo() {
    let extraInfoBox = document.getElementById("extra-info-box");
    let extraInfo = extraInfoBox.value.trim();

    if (!extraInfo) {
        alert("Please enter some apartment details before sending.");
        return;
    }

    fetch(`/conversation/extra_info`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: threadId, extra_info: extraInfo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "Extra info added") {
            alert("Extra apartment info sent!");
            extraInfoBox.value = ""; // Clear the input field after sending
            loadConversation(); // Refresh to show new info
        } else {
            alert("Error sending extra info: " + data.error);
        }
    })
    .catch(error => console.error("Error sending extra info:", error));
}

window.onload = loadConversation;
