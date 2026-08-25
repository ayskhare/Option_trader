const OWNER = process.env.GITHUB_OWNER;
const REPO = process.env.GITHUB_REPO;
const TOKEN = process.env.GITHUB_TOKEN;


async function githubRequest(url, options = {}) {

  const response = await fetch(url, {
    ...options,

    headers: {
      "Accept": "application/vnd.github+json",
      "Authorization": `Bearer ${TOKEN}`,
      "X-GitHub-Api-Version": "2022-11-28",

      ...(options.headers || {})
    }
  });

  return response;
}


exports.handler = async function (event) {

  try {

    const body = JSON.parse(
      event.body || "{}"
    );

    const {
      action = "trigger",
      workflow
    } = body;


    // ─────────────────────────────────────────
    // TRIGGER WORKFLOW
    // ─────────────────────────────────────────

    if (action === "trigger") {

      if (!workflow) {

        return {
          statusCode: 400,

          body: JSON.stringify({
            success: false,
            error: "Workflow name is required"
          })
        };
      }

      const response = await githubRequest(
        `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${workflow}/dispatches`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            ref: "main"
          })
        }
      );

      if (!response.ok) {

        const error = await response.text();

        throw new Error(error);
      }

      return {
        statusCode: 200,

        body: JSON.stringify({
          success: true,
          workflow
        })
      };
    }


    // ─────────────────────────────────────────
    // GET LATEST WORKFLOW STATUS
    // ─────────────────────────────────────────

    if (action === "status") {

      if (!workflow) {

        return {
          statusCode: 400,

          body: JSON.stringify({
            success: false,
            error: "Workflow name is required"
          })
        };
      }

      const response = await githubRequest(
        `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${workflow}/runs?per_page=1`
      );

      if (!response.ok) {

        const error = await response.text();

        throw new Error(error);
      }

      const data = await response.json();

      const run = data.workflow_runs?.[0];

      if (!run) {

        return {
          statusCode: 200,

          body: JSON.stringify({
            success: true,
            run: null
          })
        };
      }

      return {
        statusCode: 200,

        body: JSON.stringify({
          success: true,

          run: {
            id: run.id,
            status: run.status,
            conclusion: run.conclusion,
            created_at: run.created_at,
            updated_at: run.updated_at,
            html_url: run.html_url
          }
        })
      };
    }


    // ─────────────────────────────────────────
    // GET JOB LOGS
    // ─────────────────────────────────────────

    if (action === "logs") {

      if (!workflow) {

        return {
          statusCode: 400,

          body: JSON.stringify({
            success: false,
            error: "Workflow name is required"
          })
        };
      }

      const runsResponse = await githubRequest(
        `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${workflow}/runs?per_page=1`
      );

      const runsData =
        await runsResponse.json();

      const run =
        runsData.workflow_runs?.[0];

      if (!run) {

        return {
          statusCode: 200,

          body: JSON.stringify({
            success: true,
            status: "not_found",
            logs: ""
          })
        };
      }

      const jobsResponse = await githubRequest(
        `https://api.github.com/repos/${OWNER}/${REPO}/actions/runs/${run.id}/jobs`
      );

      const jobsData =
        await jobsResponse.json();

      let logs = [];

      for (const job of jobsData.jobs || []) {

        logs.push(
          `========== ${job.name} ==========`
        );

        for (
          const step of job.steps || []
        ) {

          const icon =
            step.conclusion === "success"
              ? "✅"
              : step.conclusion === "failure"
              ? "❌"
              : step.status === "in_progress"
              ? "⏳"
              : "•";

          logs.push(
            `${icon} ${step.name} — ${step.status}`
          );
        }
      }

      return {
        statusCode: 200,

        body: JSON.stringify({
          success: true,

          status: run.status,

          conclusion: run.conclusion,

          logs: logs.join("\n")
        })
      };
    }


    return {
      statusCode: 400,

      body: JSON.stringify({
        success: false,
        error: "Invalid action"
      })
    };

  } catch (error) {

    return {
      statusCode: 500,

      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
