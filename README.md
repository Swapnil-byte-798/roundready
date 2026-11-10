# RoundReady

Resume-aware interview practice with evidence behind each feedback score.

[![Python verification](https://github.com/Swapnil-byte-798/roundready/actions/workflows/ci.yml/badge.svg)](https://github.com/Swapnil-byte-798/roundready/actions/workflows/ci.yml)

Project 7 in a Python and SQL AI engineering portfolio. The interface is a Python CLI and FastAPI's generated API documentation.

## What works

- Resume-grounded question plans with verbatim resume evidence
- Content, structure and communication rubrics with answer evidence
- Ordered interview sessions, idempotent answers and quota reservations
- Account token isolation and signed, replay-safe Stripe test webhooks

## Run it

Python 3.11 or 3.12. No paid billing account is required for local practice or unit tests.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
python -m roundready demo
python -m roundready setup
python -m roundready serve --port 8020
```

Open http://127.0.0.1:8020/docs. `setup` prompts for credentials without displaying them, generates independent operator/reviewer tokens, and stores them in an ignored file with owner-only permissions. Use the operator token as `Authorization: Bearer ...`; account, client and tenant endpoints issue their own scoped tokens. Do not commit any of these values.

The demo is explicitly labelled: authored fixtures exercise the workflow, not a live provider. `check-keys` reports configuration only and never claims a provider has been validated.

## Credentials

GROQ_API_KEY for questions and feedback. STRIPE_WEBHOOK_SECRET is optional for signed test billing events.

To reuse a provider key across these repositories, run `python -m roundready setup --shared` before the local `setup` command. The shared prompt adds missing keys and preserves existing nonempty keys. Local environment variables take precedence. See [.env.example](.env.example) for names only; real keys are never shipped.

## Design and boundaries

Resume text and role → grounded question plan → candidate answer → rubric validation → computed score → progress report

This is interview coaching, not automated hiring or candidate selection. Rubric scores have not been calibrated against human raters. Input is resume text and written answers; OAuth, voice interviews, hosted checkout and real payments are outside this version. Billing accepts test-mode events only.

## Verification

Invented evidence rejection, score ranges, concurrent grading, question order, account isolation, quota rollback, webhook signatures and event replay. Common tests also cover hidden setup, configuration precedence, provider response validation, API authentication and transactional rollback.

[Verification record](evidence/verification.json) separates automated checks from provider-dependent acceptance. No result represents all possible inputs, production load, or a calibrated model-quality benchmark.

## Read further

- [Requirements and acceptance](docs/REQUIREMENTS.md)
- [Architecture and decisions](docs/ARCHITECTURE.md)
- [Runbook and key setup](docs/RUNBOOK.md)
- [Study guide](docs/STUDY_GUIDE.md)

## Next engineering milestone

Compare feedback with a labelled human rubric and add accessible audio input only after measuring transcription errors.
