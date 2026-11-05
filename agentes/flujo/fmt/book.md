OUTPUT FORMAT:
# <Book> - lessons for clean, well-organized code
## Chapter map (chapter -> topic, 1 line each)
## Lessons (numbered L-<TASKID>-NN; each: lesson as one imperative sentence; why it matters; short verbatim example or paraphrased code pattern; page reference; applies-to tag: general|python|django|postgres|testing|security|deploy)
## Project structure recommended by the book (trees)
## Conflicts with common best practice (if any)
Focus on actionable code-quality and architecture lessons, not installation steps. Extract real content, not only the table of contents. Use a scratch Python script with pypdf or pdftotext if available (do NOT install anything; if no extractor exists, report NEED). Keep scratch files in `%TEMP%\originpass-agentes\<TASK-ID>\`.