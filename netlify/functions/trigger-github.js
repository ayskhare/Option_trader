exports.handler = async function (event) {
  try {
    const { workflow } = JSON.parse(event.body || "{}");

    if (!workflow) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          success: false,
          error: "Workflow name is required"
        })
      };
    }

    const response = await fetch(
      `https://api.github.com/repos/${process.env.GITHUB_OWNER}/${process.env.GITHUB_REPO}/actions/workflows/${workflow}/dispatches`,
      {
        method: "POST",
        headers: {
          "Accept": "application/vnd.github+json",
          "Authorization": `Bearer ${process.env.GITHUB_TOKEN}`,
          "X-GitHub-Api-Version": "2022-11-28",
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
        workflow: workflow
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
