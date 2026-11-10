import hashlib, hmac, json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from roundready.cli import FixtureCoach
from roundready.runtime import Fault
from roundready.service import InterviewService


class InterviewTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.now = 1000
        self.coach = InterviewService(
            Path(self.directory.name) / "test.db",
            FixtureCoach(),
            clock=lambda: self.now,
        )
        self.account = self.coach.create_account("Candidate")
        self.token = self.account["account_token"]

    def tearDown(self):
        self.directory.cleanup()

    def start(self, key="start"):
        return self.coach.start(self.token, "Python and SQL", "Data engineer", key)

    def answer(self, session, key="answer", answer="A transaction is atomic."):
        return self.coach.answer(
            self.token, session["id"], session["current_question"]["id"], answer, key
        )

    def test_resume_grounded_plan(self):
        session = self.start()
        self.assertEqual(session["question_count"], 3)
        self.assertNotIn("expected_points", session["current_question"])

    def test_answer_advances_one_question(self):
        session = self.start()
        self.answer(session)
        self.assertEqual(self.coach.get(self.token, session["id"])["position"], 1)

    def test_duplicate_answer_does_not_advance_twice(self):
        session = self.start()
        first = self.answer(session)
        second = self.answer(session)
        self.assertEqual(first, second)
        self.assertEqual(self.coach.get(self.token, session["id"])["position"], 1)

    def test_answer_retry_is_payload_bound(self):
        session = self.start()
        self.answer(session)
        with self.assertRaises(Fault):
            self.answer(session, answer="A different atomic answer")

    def test_cannot_skip_question(self):
        session = self.start()
        with self.assertRaises(Fault):
            self.coach.answer(self.token, session["id"], "3", "atomic", "a")

    def test_session_is_private_to_account(self):
        session = self.start()
        other = self.coach.create_account("Other")
        with self.assertRaises(Fault):
            self.coach.get(other["account_token"], session["id"])

    def test_free_quota_is_enforced(self):
        for index in range(3):
            self.start(str(index))
        with self.assertRaises(Fault):
            self.start("four")

    def test_failed_plan_releases_quota(self):
        class BadCoach:
            def ask(self, *a):
                raise Fault("Provider unavailable", 502)

        self.coach.llm = BadCoach()
        with self.assertRaises(Fault):
            self.start()
        self.assertEqual(self.coach.account(self.token)["used"], 0)

    def test_invented_resume_skill_is_rejected(self):
        class BadCoach(FixtureCoach):
            def ask(self, *args):
                value = super().ask(*args)
                for question in value["questions"]:
                    question["resume_evidence"] = "Invented Kubernetes expertise"
                return value

        self.coach.llm = BadCoach()
        with self.assertRaises(Fault):
            self.start()

    def test_invented_grading_quote_does_not_advance(self):
        session = self.start()
        with self.assertRaises(Fault):
            self.answer(session, answer="No matching evidence")
        self.assertEqual(self.coach.get(self.token, session["id"])["position"], 0)

    def test_complete_interview_report(self):
        session = self.start()
        for index in range(3):
            self.answer(session, key=str(index))
            session = self.coach.get(self.token, session["id"])
        self.assertEqual(session["state"], "complete")
        self.assertEqual(len(session["feedback"]), 3)

    def event(self, identifier="evt_test", livemode=False, created=1000):
        return {
            "id": identifier,
            "created": created,
            "livemode": livemode,
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "payment_status": "paid",
                    "mode": "subscription",
                    "metadata": {"account_id": self.account["id"]},
                }
            },
        }

    def signed(self, event, timestamp=1000):
        body = json.dumps(event).encode()
        signature = hmac.new(
            b"test-signing-secret",
            str(timestamp).encode() + b"." + body,
            hashlib.sha256,
        ).hexdigest()
        return body, f"t={timestamp},v1={signature}"

    def test_signed_test_event_upgrades_plan_once(self):
        body, signature = self.signed(self.event())
        self.assertFalse(
            self.coach.billing_event(body, signature, "test-signing-secret")[
                "duplicate"
            ]
        )
        self.assertTrue(
            self.coach.billing_event(body, signature, "test-signing-secret")[
                "duplicate"
            ]
        )
        self.assertEqual(self.coach.account(self.token)["plan"], "practice")

    def test_live_money_event_is_rejected(self):
        body, signature = self.signed(self.event(livemode=True))
        with self.assertRaises(Fault):
            self.coach.billing_event(body, signature, "test-signing-secret")

    def test_invalid_signature_is_rejected(self):
        body, signature = self.signed(self.event())
        with self.assertRaises(Fault):
            self.coach.billing_event(body, signature, "wrong-secret")

    def test_stale_event_is_rejected(self):
        body, signature = self.signed(self.event(), timestamp=1)
        with self.assertRaises(Fault):
            self.coach.billing_event(body, signature, "test-signing-secret")

    def test_event_id_cannot_be_reused_with_different_payload(self):
        body, signature = self.signed(self.event())
        self.coach.billing_event(body, signature, "test-signing-secret")
        body, signature = self.signed(self.event(created=1001))
        with self.assertRaises(Fault):
            self.coach.billing_event(body, signature, "test-signing-secret")

    def test_start_retry_does_not_consume_quota(self):
        self.start()
        self.start()
        self.assertEqual(self.coach.account(self.token)["used"], 1)

    def test_average_score_is_calculated_in_python(self):
        self.assertEqual(self.answer(self.start())["average_score"], 3.0)
