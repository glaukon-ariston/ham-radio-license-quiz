# Add home button on every page

prio:       P2
cluster:    quiz-app-ui
files:      quiz/quiz.html
blocked-by:

**Why.** There's no consistent way back to the home/start screen from inside practice,
simulated exam, review, or results views except the browser back button, which can drop
in-progress state. [[ham-quiz-work-queue]] item P2-0039 already turned the in-quiz
breadcrumb into a practice-entry point, so a home affordance fits naturally next to it.

**Done when.** Every screen (practice, simulated exam, review, results, and any settings
page) shows a home button/link at the top, integrated into the existing breadcrumb bar
where one exists, that returns to the home screen. Leaving an in-progress simulated exam
via this button gives the same confirm-before-losing-progress prompt as other exit paths
(see P1-0038 — don't reintroduce that no-op-confirm bug).

**Avoid.** Don't add a second, differently-styled nav element competing with the
breadcrumb — integrate into it. Don't bypass the exam-exit confirmation dialog.
