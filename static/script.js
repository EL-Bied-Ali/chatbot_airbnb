// ✅ Detect URL parameters
let urlParams = new URLSearchParams(window.location.search);
let rawThreadId = urlParams.get("thread");
let aiResponseParam = urlParams.get("response"); // AI response from Pushbullet

// ✅ Extract only the numeric thread ID
let threadMatch = rawThreadId.match(/thread\/(\d+)/);
let threadId = threadMatch ? threadMatch[1] : rawThreadId;

console.log("🔍 Extracted Thread ID:", threadId);

// ✅ Load the correct conversation from the API
function loadConversation() {
    fetch(`/conversation?thread=${threadId}`)
        .then(response => response.json())
        .then(data => {
            console.log("📩 Debug: Full Conversation History:", data);

            let historyDiv = document.getElementById("conversation-history");

            if (data.length > 0) {
                historyDiv.innerHTML = data.map(msg =>
                    `<p><b>${msg.sender} (${msg.role}):</b> ${msg.message} 
                    <small>${new Date(msg.timestamp).toLocaleString()}</small></p>`).join('');
            } else {
                historyDiv.innerHTML = "<p>No messages yet.</p>";
            }

            // ✅ Prefill AI response in the text box BEFORE approval
            let aiResponseBox = document.getElementById("ai-response-box");

            if (aiResponseParam) {
                console.log("✅ Prefilling AI response from Pushbullet:", aiResponseParam);
                aiResponseBox.value = decodeURIComponent(aiResponseParam);
            } else {
                // ✅ If no response from Pushbullet, generate it dynamically
                fetch(`/generate_ai_response?thread=${threadId}`)
                    .then(response => response.json())
                    .then(aiData => {
                        console.log("✅ AI response dynamically generated:", aiData.response);
                        aiResponseBox.value = aiData.response;
                    })
                    .catch(error => console.error("Error generating AI response:", error));
            }
        })
        .catch(error => console.error("Error loading conversation:", error));
}

// ✅ Load conversation on page load
window.onload = function () {
    loadConversation();
};

// ✅ Save the edited AI response (stores in `conversations.json`)
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
            copyToClipboard(editedMessage);
            console.log("✅ AI response saved successfully.");
        } else {
            alert("Error saving response: " + data.error);
        }
    })
    .catch(error => console.error("Error saving response:", error));
}
