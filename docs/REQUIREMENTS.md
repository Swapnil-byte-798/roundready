# RoundReady: requirements and acceptance

## Product goal

Resume-aware interview practice with evidence behind each feedback score. A reviewer should be able to install the package, run its tests, inspect its SQL boundaries and exercise the core workflow without a custom frontend.

## Functional requirements

- Resume-grounded question plans with verbatim resume evidence
- Content, structure and communication rubrics with answer evidence
- Ordered interview sessions, idempotent answers and quota reservations
- Account token isolation and signed, replay-safe Stripe test webhooks

## Acceptance conditions

1. Question evidence must occur in the supplied resume.
2. Feedback evidence must occur in the candidate's answer.
3. A failed planning call restores the reserved interview quota.
4. A duplicate billing event or answer cannot apply twice.

## Quality requirements

Persist domain state transactionally; validate untrusted inputs; keep provider failures visible; avoid credential and prompt disclosure in diagnostic errors; provide an installable Python package, authenticated API, container and repeatable automated checks. Keep fixture evidence distinct from public-data and live-provider evidence.

## Scope boundary

This is interview coaching, not automated hiring or candidate selection. Rubric scores have not been calibrated against human raters. Input is resume text and written answers; OAuth, voice interviews, hosted checkout and real payments are outside this version. Billing accepts test-mode events only.

## Evaluation plan

Invented evidence rejection, score ranges, concurrent grading, question order, account isolation, quota rollback, webhook signatures and event replay. External checks need the credentials, model files or network access described in the runbook. Before publishing quality claims, create a labelled evaluation set and report sample size, metric definition, model version and measured failures. Compare feedback with a labelled human rubric and add accessible audio input only after measuring transcription errors.
