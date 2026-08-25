const updateDataBtn = document.getElementById("updateDataBtn");
const testConnectionBtn = document.getElementById("testConnectionBtn");
const activityMessage = document.getElementById("activityMessage");

async function triggerGitHubWorkflow(workflow) {
    try {
        const response = await fetch("/.netlify/functions/trigger-github", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                workflow: workflow
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Something went wrong");
        }

        return result;

    } catch (error) {
        throw error;
    }
}


testConnectionBtn.addEventListener("click", async () => {

    activityMessage.textContent =
        "Testing Angel One connection...";

    testConnectionBtn.disabled = true;

    try {

        await triggerGitHubWorkflow(
            "test-connection.yml"
        );

        activityMessage.textContent =
            "Connection test started successfully. Check GitHub Actions.";

    } catch (error) {

        activityMessage.textContent =
            "Connection test failed: " + error.message;

    }

    testConnectionBtn.disabled = false;

});


updateDataBtn.addEventListener("click", async () => {

    activityMessage.textContent =
        "Starting historical data update...";

    updateDataBtn.disabled = true;

    try {

        await triggerGitHubWorkflow(
            "update-data.yml"
        );

        activityMessage.textContent =
            "Historical data update started successfully. Check GitHub Actions.";

    } catch (error) {

        activityMessage.textContent =
            "Historical data update failed: " + error.message;

    }

    updateDataBtn.disabled = false;

});
