let sessionId = null;
let questionNumber = 0;
const totalQuestions = 8;


// -------------------------
// DOM Elements
// -------------------------

const startScreen = document.getElementById("start-screen");
const interviewScreen = document.getElementById("interview-screen");
const completeScreen = document.getElementById("complete-screen");

const candidateInput = document.getElementById("candidate-id");
const startButton = document.getElementById("start-btn");
const submitButton = document.getElementById("submit-btn");

const questionText = document.getElementById("question-text");
const answerInput = document.getElementById("answer-input");

const questionCounter = document.getElementById("question-counter");
const progressFill = document.getElementById("progress-fill");

const startError = document.getElementById("start-error");
const interviewError = document.getElementById("interview-error");
const answerStatus = document.getElementById("answer-status");

const feedbackSummary = document.getElementById("feedback-summary");
const strengthsList = document.getElementById("strengths-list");
const gapsList = document.getElementById("gaps-list");
const nextStepText = document.getElementById("next-step-text");


// -------------------------
// Utility
// -------------------------

function generateSessionId() {
    return "session-" + Date.now();
}


function showScreen(screen) {
    startScreen.classList.add("hidden");
    interviewScreen.classList.add("hidden");
    completeScreen.classList.add("hidden");

    screen.classList.remove("hidden");
}


function updateProgress() {
    questionCounter.textContent =
        `Question ${questionNumber} / ${totalQuestions}`;

    const percentage =
        (questionNumber / totalQuestions) * 100;

    progressFill.style.width = `${percentage}%`;
}


function setLoading(button, loading, originalText) {
    button.disabled = loading;

    if (loading) {
        button.innerHTML = "Thinking...";
    } else {
        button.innerHTML = `${originalText} <span>→</span>`;
    }
}


// -------------------------
// Start Interview
// -------------------------

startButton.addEventListener("click", startInterview);


async function startInterview() {

    const candidateId = candidateInput.value.trim();

    startError.textContent = "";

    if (!candidateId) {
        startError.textContent =
            "Please enter a candidate ID.";

        return;
    }

    sessionId = generateSessionId();

    setLoading(
        startButton,
        true,
        "Start Interview"
    );

    try {

        const response = await fetch("/api/interview", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                sessionId: sessionId,
                candidate: candidateId
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error || "Failed to start interview."
            );
        }


        if (!data.reply) {
            throw new Error(
                "Interview API returned no question."
            );
        }


        questionNumber = 1;

        questionText.textContent = data.reply;

        answerInput.value = "";

        updateProgress();

        showScreen(interviewScreen);

        answerInput.focus();

    } catch (error) {

        console.error("Start interview error:", error);

        startError.textContent =
            error.message ||
            "Unable to start the interview.";

    } finally {

        setLoading(
            startButton,
            false,
            "Start Interview"
        );
    }
}


// -------------------------
// Submit Answer
// -------------------------

submitButton.addEventListener("click", submitAnswer);


async function submitAnswer() {

    const answer = answerInput.value.trim();

    interviewError.textContent = "";

    if (!answer) {

        interviewError.textContent =
            "Please enter an answer before submitting.";

        answerInput.focus();

        return;
    }


    if (!sessionId) {

        interviewError.textContent =
            "Interview session is missing. Please restart.";

        return;
    }


    setLoading(
        submitButton,
        true,
        "Submit Answer"
    );

    answerStatus.textContent =
        "Evaluating your answer...";


    try {

        const response = await fetch("/api/interview", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                sessionId: sessionId,
                message: answer
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error || "Failed to process answer."
            );
        }


        // Interview completed
        if (data.done === true) {

            showFeedback(data.feedback);

            return;
        }


        // Continue interview
        if (!data.reply) {

            throw new Error(
                "Interview API returned no next question."
            );
        }


        questionNumber++;

        questionText.textContent = data.reply;

        answerInput.value = "";

        updateProgress();

        answerStatus.textContent =
            "Be clear and explain your reasoning.";

        answerInput.focus();


    } catch (error) {

        console.error("Submit answer error:", error);

        interviewError.textContent =
            error.message ||
            "Unable to process your answer.";

        answerStatus.textContent =
            "Something went wrong. Try again.";

    } finally {

        setLoading(
            submitButton,
            false,
            "Submit Answer"
        );
    }
}


// -------------------------
// Final Feedback
// -------------------------

function showFeedback(feedback) {

    if (!feedback) {

        feedback = {
            summary:
                "Your interview has been completed.",
            strengths: [],
            gaps: [],
            next:
                "Review the topics covered during the interview."
        };
    }


    feedbackSummary.textContent =
        feedback.summary || "Interview completed.";


    strengthsList.innerHTML = "";

    const strengths =
        feedback.strengths || [];

    strengths.forEach(strength => {

        const li = document.createElement("li");

        li.textContent = strength;

        strengthsList.appendChild(li);
    });


    gapsList.innerHTML = "";

    const gaps =
        feedback.gaps || [];

    gaps.forEach(gap => {

        const li = document.createElement("li");

        li.textContent = gap;

        gapsList.appendChild(li);
    });


    nextStepText.textContent =
        feedback.next ||
        "Continue strengthening the areas covered in the interview.";


    showScreen(completeScreen);
}