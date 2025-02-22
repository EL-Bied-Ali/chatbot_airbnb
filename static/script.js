// ✅ Detect URL parameters
let urlParams = new URLSearchParams(window.location.search);
let rawThreadId = urlParams.get("thread");
let aiResponseParam = urlParams.get("response"); // AI response from Pushbullet

// ✅ Extract only the numeric thread ID
let threadMatch = rawThreadId.match(/thread\/(\d+)/);
let threadId = threadMatch ? threadMatch[1] : rawThreadId;

console.log("🔍 Extracted Thread ID:", threadId);

// ✅ Load conversation history
function loadConversation() {
    console.log("🔍 Fetching conversation for thread:", threadId);

    fetch(`/conversation?thread=${threadId}`)
        .then(response => response.json())
        .then(data => {
            console.log("📩 Debug: Full Conversation History:", data);

            let historyDiv = document.getElementById("conversation-history");
            if (!historyDiv) {
                console.error("❌ Error: 'conversation-history' element not found in HTML!");
                return;
            }

            if (data && Array.isArray(data) && data.length > 0) {
                historyDiv.innerHTML = data.map(msg =>
                    `<p><b>${msg.sender} (${msg.role}):</b> ${msg.message} 
                    <small>${new Date(msg.timestamp).toLocaleString()}</small></p>`).join('');
            } else {
                historyDiv.innerHTML = "<p>No messages yet.</p>";
            }

            let aiResponseBox = document.getElementById("ai-response-box");
            if (!aiResponseBox) {
                console.error("❌ Error: 'ai-response-box' element not found in HTML!");
                return;
            }

            if (aiResponseParam) {
                console.log("✅ Prefilling AI response from Pushbullet:", aiResponseParam);
                aiResponseBox.value = decodeURIComponent(aiResponseParam);
            } else {
                fetch(`/generate_ai_response?thread=${threadId}`)
                    .then(response => response.json())
                    .then(aiData => {
                        console.log("✅ AI response dynamically generated:", aiData.response);
                        aiResponseBox.value = aiData.response ? aiData.response : "No AI response available.";
                    })
                    .catch(error => {
                        console.error("❌ Error generating AI response:", error);
                        aiResponseBox.value = "Error loading AI response.";
                    });
            }
        })
        .catch(error => {
            console.error("❌ Error loading conversation:", error);
            document.getElementById("conversation-history").innerHTML = "<p>Error loading conversation.</p>";
        });
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

    // ✅ Ensure threadId is properly defined before proceeding
    if (typeof threadId === "undefined" || !threadId) {
        console.error("❌ Error: threadId is undefined!");
        alert("Error: Missing thread ID. Please refresh the page and try again.");
        return;
    }

    console.log("🔍 Debug: Sending AI response to API...", { threadId, editedMessage });

    fetch(`/conversation/edit_response/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id: threadId, message: editedMessage })
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Debug: API response received:", data);

        if (data.status === "Response approved and saved") {
            console.log("✅ AI response successfully saved.");

            // ✅ Copy AI response to clipboard safely
            if (navigator.clipboard) {
                navigator.clipboard.writeText(editedMessage)
                    .then(() => console.log("📋 Copied to clipboard:", editedMessage))
                    .catch(err => console.error("❌ Failed to copy:", err));
            } else {
                console.warn("⚠️ Clipboard API not supported.");
            }

            // ✅ Redirect to Airbnb messaging page safely
            setTimeout(() => {
                if (threadId) {
                    console.log("🔀 Redirecting to Airbnb:", `https://fr.airbnb.be/messaging/thread/${threadId}`);
                    window.location.href = `https://fr.airbnb.be/messaging/thread/${threadId}`;
                } else {
                    console.error("❌ Error: threadId is missing, cannot redirect.");
                }
            }, 500); // Delay for smooth transition
        } else {
            alert("Error saving response: " + (data.error || "Unknown error"));
        }
    })
    .catch(error => {
        console.error("❌ Error saving response:", error);
        alert("An error occurred while saving the response. Please try again.");
    });
}
