import tempfile
from pathlib import Path
from .runtime import run_cli
from .service import InterviewService


class FixtureCoach:
    def ask(self, instruction, payload):
        if "resume" in payload:
            return {
                "questions": [
                    {
                        "id": str(index),
                        "question": "Explain a database transaction and rollback.",
                        "topic": "SQL",
                        "resume_evidence": "Python and SQL",
                        "expected_points": ["Atomic commit", "Rollback on failure"],
                    }
                    for index in range(1, 4)
                ]
            }
        criterion = {
            "score": 3,
            "feedback": "Fixture feedback for workflow verification.",
            "evidence_quote": "atomic",
        }
        return {
            "content": criterion,
            "structure": criterion,
            "communication": criterion,
            "model_answer": "A transaction commits its changes atomically or rolls them back.",
            "next_steps": ["Practise a failure example."],
        }


def demo():
    with tempfile.TemporaryDirectory() as directory:
        coach = InterviewService(Path(directory) / "demo.db", FixtureCoach())
        account = coach.create_account("Demo candidate")
        session = coach.start(
            account["account_token"], "Python and SQL", "Data engineer", "start"
        )
        feedback = coach.answer(
            account["account_token"],
            session["id"],
            session["current_question"]["id"],
            "A transaction is atomic.",
            "answer",
        )
        return {
            "mode": "injected_coach_fixture",
            "session": coach.get(account["account_token"], session["id"]),
            "feedback": feedback,
            "live_judge_evaluated": False,
        }


def main():
    run_cli("roundready", demo, ("GROQ_API_KEY", "STRIPE_WEBHOOK_SECRET"))
