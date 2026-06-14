

/* =====================================================
   DOM ELEMENTS
===================================================== */

const questionText =
    document.getElementById(
        "questionText"
    );

const answerText =
    document.getElementById(
        "answerText"
    );

const currentQuestionLabel =
    document.getElementById(
        "currentQuestion"
    );

const progressFill =
    document.getElementById(
        "progressFill"
    );

const progressPercent =
    document.getElementById(
        "progressPercent"
    );

const prevBtn =
    document.getElementById(
        "prevBtn"
    );

const nextBtn =
    document.getElementById(
        "nextBtn"
    );

const saveBtn =
    document.getElementById(
        "saveBtn"
    );

const saveStatus =
    document.getElementById(
        "saveStatus"
    );

/* =====================================================
   ANSWERS STORAGE
===================================================== */

let answers = {};

/* =====================================================
   LOAD QUESTION
===================================================== */

function loadQuestion(index)
{
    if (
        !questions ||
        questions.length === 0
    )
    {
        return;
    }

    const question =
        questions[index];

    questionText.textContent =
        question.question_text;

    answerText.value =
        answers[question.id]
        ||
        question.answer_text
        ||
        "";

    currentQuestionLabel.textContent =
        index + 1;

    updateProgress();

    updateButtons();
}

/* =====================================================
   UPDATE PROGRESS
===================================================== */

function updateProgress()
{
    const percentage =
        (
            (currentQuestionIndex + 1)
            /
            questions.length
        ) * 100;

    progressFill.style.width =
        percentage + "%";

    progressPercent.textContent =
        Math.round(
            percentage
        ) + "%";
}

/* =====================================================
   UPDATE BUTTONS
===================================================== */

function updateButtons()
{
    prevBtn.disabled =
        currentQuestionIndex === 0;

    nextBtn.disabled =
        currentQuestionIndex ===
        questions.length - 1;
}

/* =====================================================
   PREVIOUS QUESTION
===================================================== */

prevBtn.addEventListener(
    "click",
    () =>
    {
        storeCurrentAnswer();

        if (
            currentQuestionIndex > 0
        )
        {
            currentQuestionIndex--;

            loadQuestion(
                currentQuestionIndex
            );
        }
    }
);

/* =====================================================
   NEXT QUESTION
===================================================== */

nextBtn.addEventListener(
    "click",
    () =>
    {
        storeCurrentAnswer();

        if (
            currentQuestionIndex <
            questions.length - 1
        )
        {
            currentQuestionIndex++;

            loadQuestion(
                currentQuestionIndex
            );
        }
    }
);

/* =====================================================
   STORE CURRENT ANSWER
===================================================== */

function storeCurrentAnswer()
{
    const question =
        questions[
            currentQuestionIndex
        ];

    answers[
        question.id
    ] = answerText.value;
}

/* =====================================================
   SAVE ANSWER BUTTON
===================================================== */

saveBtn.addEventListener(
    "click",
    async () =>
    {
        await saveCurrentAnswer();
    }
);

/* =====================================================
   SAVE CURRENT ANSWER
===================================================== */

async function saveCurrentAnswer()
{
    try
    {
        const question =
            questions[
                currentQuestionIndex
            ];

        const answer =
            answerText.value;

        answers[
            question.id
        ] = answer;

        saveStatus.textContent =
            "Saving...";

        saveStatus.style.color =
            "#f59e0b";

        const formData =
            new FormData();

        formData.append(
            "question_id",
            question.id
        );

        formData.append(
            "answer",
            answer
        );

        const response =
            await fetch(
                "/save-answer",
                {
                    method: "POST",
                    body: formData
                }
            );

        const result =
            await response.json();

        if(result.success)
        {
            saveStatus.textContent =
                "Saved";

            saveStatus.style.color =
                "#22c55e";
        }
        else
        {
            saveStatus.textContent =
                "Failed";

            saveStatus.style.color =
                "#ef4444";
        }
    }
    catch(error)
    {
        console.error(
            error
        );

        saveStatus.textContent =
            "Failed";

        saveStatus.style.color =
            "#ef4444";
    }
}

/* =====================================================
   LOAD EXISTING ANSWERS
===================================================== */

function loadExistingAnswers()
{
    if(
        !questions ||
        questions.length === 0
    )
    {
        return;
    }

    questions.forEach(
        (question) =>
        {
            answers[
                question.id
            ] =
            question.answer_text
            ||
            "";
        }
    );
}

/* =====================================================
   AUTO SAVE TIMER
===================================================== */

let autoSaveTimer = null;

answerText.addEventListener(
    "input",
    () =>
    {
        saveStatus.textContent =
            "Unsaved";

        saveStatus.style.color =
            "#f59e0b";

        storeCurrentAnswer();

        clearTimeout(
            autoSaveTimer
        );

        autoSaveTimer =
            setTimeout(
                async () =>
                {
                    await saveCurrentAnswer();
                },
                3000
            );
    }
);

/* =====================================================
   PAGE EXIT SAVE
===================================================== */

window.addEventListener(
    "beforeunload",
    async () =>
    {
        storeCurrentAnswer();

        await saveCurrentAnswer();
    }
);

/* =====================================================
   KEYBOARD SHORTCUTS
===================================================== */

document.addEventListener(
    "keydown",
    async (event) =>
    {
        // Ctrl + S

        if(
            event.ctrlKey &&
            event.key === "s"
        )
        {
            event.preventDefault();

            await saveCurrentAnswer();
        }

        // Left Arrow

        if(
            event.key === "ArrowLeft"
        )
        {
            if(
                currentQuestionIndex > 0
            )
            {
                storeCurrentAnswer();

                currentQuestionIndex--;

                loadQuestion(
                    currentQuestionIndex
                );
            }
        }

        // Right Arrow

        if(
            event.key === "ArrowRight"
        )
        {
            if(
                currentQuestionIndex <
                questions.length - 1
            )
            {
                storeCurrentAnswer();

                currentQuestionIndex++;

                loadQuestion(
                    currentQuestionIndex
                );
            }
        }
    }
);

/* =====================================================
   SPEECH RECOGNITION
===================================================== */

const recordBtn =
    document.getElementById(
        "recordBtn"
    );

const recordingStatus =
    document.getElementById(
        "recordingStatus"
    );

let recognition = null;

let isRecording = false;

/* =====================================================
   CHECK SUPPORT
===================================================== */

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

if (SpeechRecognition)
{
    recognition =
        new SpeechRecognition();

    recognition.continuous = true;

    recognition.interimResults = true;

    recognition.lang = "en-US";
}

/* =====================================================
   START / STOP RECORDING
===================================================== */

recordBtn.addEventListener(
    "click",
    () =>
    {
        if (!recognition)
        {
            alert(
                "Speech recognition is not supported in your browser."
            );

            return;
        }

        if (!isRecording)
        {
            startRecording();
        }
        else
        {
            stopRecording();
        }
    }
);

/* =====================================================
   START RECORDING
===================================================== */

function startRecording()
{
    isRecording = true;

    recognition.start();

    recordBtn.classList.add(
        "recording"
    );

    recordBtn.innerHTML =
        `
        <i class="fa-solid fa-stop"></i>
        Stop Recording
        `;

    recordingStatus.textContent =
        "Listening...";

    recordingStatus.classList.remove(
        "status-ready"
    );

    recordingStatus.classList.add(
        "status-recording"
    );
}

/* =====================================================
   STOP RECORDING
===================================================== */

function stopRecording()
{
    isRecording = false;

    recognition.stop();

    recordBtn.classList.remove(
        "recording"
    );

    recordBtn.innerHTML =
        `
        <i class="fa-solid fa-microphone"></i>
        Start Recording
        `;

    recordingStatus.textContent =
        "Microphone Ready";

    recordingStatus.classList.remove(
        "status-recording"
    );

    recordingStatus.classList.add(
        "status-ready"
    );
}

/* =====================================================
   SPEECH RESULT
===================================================== */

if (recognition)
{
    recognition.onresult =
        (event) =>
        {
            let transcript = "";

            for (
                let i =
                event.resultIndex;
                i <
                event.results.length;
                i++
            )
            {
                transcript +=
                    event.results[i][0]
                    .transcript;
            }

            answerText.value =
                transcript;

            storeCurrentAnswer();
        };

    recognition.onerror =
        (event) =>
        {
            console.error(
                event.error
            );

            recordingStatus.textContent =
                "Microphone Error";

            recordingStatus.classList.remove(
                "status-ready"
            );

            recordingStatus.classList.add(
                "status-recording"
            );

            stopRecording();
        };

    recognition.onend =
        () =>
        {
            if (isRecording)
            {
                recognition.start();
            }
        };
}

/* =====================================================
   INITIALIZE PAGE
===================================================== */

function initializeInterview()
{
    if (
        !questions ||
        questions.length === 0
    )
    {
        questionText.textContent =
            "No questions found.";

        return;
    }

    loadExistingAnswers();

    loadQuestion(
        currentQuestionIndex
    );

    recordingStatus.classList.add(
        "status-ready"
    );

    saveStatus.textContent =
        "Ready";

    saveStatus.style.color =
        "#22c55e";
}

/* =====================================================
   INIT
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    () =>
    {
        initializeInterview();
    }
);


