const updateDataBtn =
    document.getElementById(
        "updateDataBtn"
    );

const testConnectionBtn =
    document.getElementById(
        "testConnectionBtn"
    );

const consoleOutput =
    document.getElementById(
        "consoleOutput"
    );

const consoleStatus =
    document.getElementById(
        "consoleStatus"
    );

const systemStatus =
    document.getElementById(
        "systemStatus"
    );

const lastChecked =
    document.getElementById(
        "lastChecked"
    );


const WORKFLOWS = {

    update:
        "update_historical.yml",

    connection:
        "test_connection.yml"

};


function setConsole(text) {

    consoleOutput.textContent = text;

    consoleOutput.scrollTop =
        consoleOutput.scrollHeight;

}


function appendConsole(text) {

    consoleOutput.textContent +=
        "\n" + text;

    consoleOutput.scrollTop =
        consoleOutput.scrollHeight;

}


async function callGitHubFunction(
    action,
    workflow
) {

    const response = await fetch(
        "/.netlify/functions/trigger-github",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                action,
                workflow
            })
        }
    );

    const result =
        await response.json();

    if (!response.ok) {

        throw new Error(
            result.error ||
            "Request failed"
        );
    }

    return result;

}


async function triggerWorkflow(
    workflow,
    title
) {

    try {

        setConsole(
            `Option Trader Console\n\n` +
            `${title}\n` +
            `${"=".repeat(50)}\n\n` +
            `Sending request to GitHub Actions...`
        );

        consoleStatus.textContent =
            "Starting...";

        systemStatus.textContent =
            "Workflow Starting";

        await callGitHubFunction(
            "trigger",
            workflow
        );

        appendConsole(
            "Workflow started successfully."
        );

        appendConsole(
            "Waiting for GitHub Actions..."
        );

        await new Promise(
            resolve =>
                setTimeout(resolve, 3000)
        );

        monitorWorkflow(workflow);

    } catch (error) {

        appendConsole(
            `\nERROR: ${error.message}`
        );

        consoleStatus.textContent =
            "Failed";

        systemStatus.textContent =
            "Error";

        throw error;
    }

}


async function monitorWorkflow(
    workflow
) {

    let finished = false;

    while (!finished) {

        try {

            const statusResult =
                await callGitHubFunction(
                    "status",
                    workflow
                );

            const logResult =
                await callGitHubFunction(
                    "logs",
                    workflow
                );

            if (
                logResult.logs
            ) {

                setConsole(
                    `Option Trader Console\n\n` +
                    logResult.logs
                );

            }


            const run =
                statusResult.run;


            if (!run) {

                appendConsole(
                    "\nWaiting for workflow to start..."
                );

                await new Promise(
                    resolve =>
                        setTimeout(
                            resolve,
                            3000
                        )
                );

                continue;

            }


            if (
                run.status ===
                "in_progress"
            ) {

                consoleStatus.textContent =
                    "Running ⏳";

                systemStatus.textContent =
                    "Workflow Running";

            }


            if (
                run.status ===
                "queued"
            ) {

                consoleStatus.textContent =
                    "Queued";

            }


            if (
                run.status ===
                "completed"
            ) {

                finished = true;

                if (
                    run.conclusion ===
                    "success"
                ) {

                    consoleStatus.textContent =
                        "Completed ✅";

                    systemStatus.textContent =
                        "System Ready";

                    appendConsole(
                        "\n\nWorkflow completed successfully ✅"
                    );

                    loadLatestDates();

                } else {

                    consoleStatus.textContent =
                        "Failed ❌";

                    systemStatus.textContent =
                        "Workflow Failed";

                    appendConsole(
                        `\n\nWorkflow failed: ${run.conclusion}`
                    );

                }

            }

        } catch (error) {

            appendConsole(
                `\nConsole monitoring error: ${error.message}`
            );

        }


        if (!finished) {

            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        3000
                    )
            );

        }

    }

}


updateDataBtn.addEventListener(
    "click",
    async () => {

        updateDataBtn.disabled = true;

        testConnectionBtn.disabled = true;

        try {

            await triggerWorkflow(
                WORKFLOWS.update,
                "Historical Data Update"
            );

        } finally {

            updateDataBtn.disabled = false;

            testConnectionBtn.disabled = false;

        }

    }
);


testConnectionBtn.addEventListener(
    "click",
    async () => {

        testConnectionBtn.disabled = true;

        updateDataBtn.disabled = true;

        try {

            await triggerWorkflow(
                WORKFLOWS.connection,
                "Angel One Connection Test"
            );

        } finally {

            testConnectionBtn.disabled = false;

            updateDataBtn.disabled = false;

        }

    }
);


/* ────────────────────────────────────────────
   LOAD LATEST CSV DATES
──────────────────────────────────────────── */

async function loadLatestDate(
    file,
    elementId
) {

    try {

        const response =
            await fetch(
                `data/${file}?t=${Date.now()}`
            );

        if (!response.ok) {
            throw new Error();
        }

        const text =
            await response.text();

        const lines =
            text.trim()
                .split("\n");

        if (lines.length < 2) {
            throw new Error();
        }

        const lastLine =
            lines[lines.length - 1];

        const firstValue =
            lastLine.split(",")[0];

        const date =
            new Date(firstValue);

        const formatted =
            date.toLocaleDateString(
                "en-IN",
                {
                    day: "2-digit",
                    month: "short",
                    year: "numeric"
                }
            );

        document.getElementById(
            elementId
        ).textContent =
            formatted;

    } catch {

        document.getElementById(
            elementId
        ).textContent =
            "Unavailable";

    }

}


async function loadLatestDates() {

    await Promise.all([

        loadLatestDate(
            "nifty50_daily.csv",
            "nifty50Date"
        ),

        loadLatestDate(
            "banknifty_daily.csv",
            "bankNiftyDate"
        ),

        loadLatestDate(
            "nifty_midcap50_daily.csv",
            "midcapDate"
        ),

        loadLatestDate(
            "nifty_vix.csv",
            "vixDate"
        )

    ]);

    lastChecked.textContent =
        `Last checked: ${new Date()
            .toLocaleString("en-IN")}`;

}


loadLatestDates();
