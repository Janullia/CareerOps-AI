#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path

from workflow_state import initial_state, transition, validate_state


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.state = initial_state("execucao", "candidata")

    def tearDown(self):
        self.temp.cleanup()

    def artifact(self, name, candidate_id="candidata", errors=0):
        path = self.base / name
        path.write_text(
            json.dumps({"candidate_id": candidate_id, "summary": {"errors": errors}}),
            encoding="utf-8",
        )
        return str(path)

    def complete(self, stage):
        transition(self.state, stage, "in_progress")
        transition(self.state, stage, "completed", artifact=self.artifact(f"{stage}.json"))

    def test_initial_stage_is_profile(self):
        self.assertEqual(self.state["current_stage"], "profile")

    def test_jobs_cannot_start_before_profile(self):
        with self.assertRaises(ValueError):
            transition(self.state, "jobs", "in_progress")

    def test_match_requires_profile_and_jobs(self):
        self.complete("profile")
        with self.assertRaises(ValueError):
            transition(self.state, "match", "in_progress")

    def test_bundle_requires_match(self):
        self.complete("profile")
        self.complete("jobs")
        with self.assertRaises(ValueError):
            transition(self.state, "bundle", "in_progress")

    def test_completed_stage_requires_artifact(self):
        transition(self.state, "profile", "in_progress")
        with self.assertRaises(ValueError):
            transition(self.state, "profile", "completed")

    def test_rejects_mixed_candidate_artifact(self):
        transition(self.state, "profile", "in_progress")
        with self.assertRaises(ValueError):
            transition(
                self.state,
                "profile",
                "completed",
                artifact=self.artifact("outro.json", candidate_id="outra-candidata"),
            )

    def test_rejects_artifact_with_validation_errors(self):
        transition(self.state, "profile", "in_progress")
        with self.assertRaises(ValueError):
            transition(
                self.state,
                "profile",
                "completed",
                artifact=self.artifact("erro.json", errors=1),
            )

    def test_blocked_stage_can_resume(self):
        transition(self.state, "profile", "blocked", note="Currículo ausente")
        transition(self.state, "profile", "in_progress")
        self.assertEqual(self.state["stages"]["profile"]["status"], "in_progress")

    def test_completed_stage_cannot_regress(self):
        self.complete("profile")
        with self.assertRaises(ValueError):
            transition(self.state, "profile", "in_progress")

    def test_approval_requires_explicit_flag(self):
        for stage in ("profile", "jobs", "match", "bundle"):
            self.complete(stage)
        transition(self.state, "approval", "in_progress")
        with self.assertRaises(ValueError):
            transition(self.state, "approval", "completed")

    def test_explicit_approval_is_recorded(self):
        for stage in ("profile", "jobs", "match", "bundle"):
            self.complete(stage)
        transition(self.state, "approval", "in_progress")
        transition(self.state, "approval", "completed", user_approved=True, note="Aprovação explícita")
        self.assertTrue(self.state["stages"]["approval"]["user_approved"])
        self.assertTrue(self.state["events"][-1]["user_approved"])

    def test_missing_guardrail_invalidates_state(self):
        self.state["guardrails"]["application_requires_approval"] = False
        self.assertTrue(validate_state(self.state))

    def test_full_technical_pipeline_is_valid_with_approval_pending(self):
        for stage in ("profile", "jobs", "match", "bundle"):
            self.complete(stage)
        self.assertEqual(self.state["current_stage"], "approval")
        self.assertEqual(validate_state(self.state), [])

    def test_transitions_are_recorded(self):
        before = len(self.state["events"])
        transition(self.state, "profile", "in_progress", note="Começo")
        self.assertEqual(len(self.state["events"]), before + 1)


if __name__ == "__main__":
    unittest.main()
