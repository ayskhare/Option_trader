const updateDataBtn = document.getElementById("updateDataBtn");
const testConnectionBtn = document.getElementById("testConnectionBtn");
const activityMessage = document.getElementById("activityMessage");


updateDataBtn.addEventListener("click", () => {

    activityMessage.textContent =
        "Update Historical Data button clicked. GitHub integration coming next.";

});


testConnectionBtn.addEventListener("click", () => {

    activityMessage.textContent =
        "Test Angel One Connection button clicked. GitHub integration coming next.";

});
