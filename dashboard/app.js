const updateDataBtn = document.getElementById("updateDataBtn");
const testConnectionBtn = document.getElementById("testConnectionBtn");
const activityMessage = document.getElementById("activityMessage");


// ─────────────────────────────────────────────
// Update Historical Data
// Placeholder for now
// ─────────────────────────────────────────────

updateDataBtn.addEventListener("click", () => {

    activityMessage.textContent =
        "Update Historical Data integration coming next.";

});


// ─────────────────────────────────────────────
// Test Angel One Connection
// ─────────────────────────────────────────────

testConnectionBtn.addEventListener("click", async () => {

    activityMessage.textContent =
        "Testing Angel One connection...";

    try {

        const response = await fetch(
            "/.netlify/functions/trigger-github",
            {
                method: "POST"
            }
        );

        const result = await response.json();

        if (result.success) {

            activityMessage.textContent =
                "Connection test started successfully. Check GitHub Actions.";

        } else {

            activityMessage.textContent =
                "Failed: " + result.error;

        }

    } catch (error) {

        activityMessage.textContent =
            "Error: " + error.message;

    }

});
