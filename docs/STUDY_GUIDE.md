# RoundReady: study guide

## Explain the problem

Resume-aware interview practice with evidence behind each feedback score. Explain who uses the workflow and why each confirmation, isolation or validation boundary exists before describing libraries.

## Read the implementation

1. Read `service.py` and its SQL schema. Name the durable entities and draw their valid state transitions.
2. Trace one successful API request from its Pydantic input to its committed writes.
3. Trace a provider failure and identify what can and cannot be rolled back.
4. Read the tests that enforce the acceptance conditions below. Explain why each failure would matter to a user.

1. Question evidence must occur in the supplied resume.
2. Feedback evidence must occur in the candidate's answer.
3. A failed planning call restores the reserved interview quota.
4. A duplicate billing event or answer cannot apply twice.

## Interview discussion

- Where is the transaction boundary, and what happens if the process dies immediately after it?
- How are retries bound to the original request? Which operation can safely repeat?
- Which inputs are untrusted, and how are externally generated fields validated?
- What is tested with fixtures, what was measured on public data, and what remains unmeasured?
- What would change with ten times the data, multiple workers, or another tenant?

## Honest project explanation

Describe the implemented behavior, then demonstrate a representative test and explain its failure condition. Do not present mock latency, authored examples, uncalibrated scores or optional integrations as measured production results.

Known boundaries: This is interview coaching, not automated hiring or candidate selection. Rubric scores have not been calibrated against human raters. Input is resume text and written answers; OAuth, voice interviews, hosted checkout and real payments are outside this version. Billing accepts test-mode events only.

## Practical extension

Compare feedback with a labelled human rubric and add accessible audio input only after measuring transcription errors. Define a measurable acceptance criterion before extending the implementation.
