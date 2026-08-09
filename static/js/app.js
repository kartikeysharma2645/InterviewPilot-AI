const startScreen = document.getElementById("start-screen");
const interviewScreen = document.getElementById("interview-screen");
const completeScreen = document.getElementById("complete-screen");

const startButton = document.getElementById("start-btn");

startButton.addEventListener("click", () => {
    const candidateId =
        document.getElementById("candidate-id").value.trim();

    if (!candidateId) {
        document.getElementById("start-error").textContent =
            "Please enter a candidate ID.";

        return;
    }

    startScreen.classList.add("hidden");
    interviewScreen.classList.remove("hidden");
});