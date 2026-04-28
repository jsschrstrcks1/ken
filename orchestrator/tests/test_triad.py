#!/usr/bin/env python3
"""Tests for the triad mode and the orchestrate plumbing it depends on.

These tests stub the external adapters so the suite runs offline. They
verify role wiring, prompt threading (verifier verdict reaches planner on
revision), and convergence on terminal verdicts.

Run: python3 orchestrator/tests/test_triad.py
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

# Import after sys.path is set.
import orchestrate  # noqa: E402
import consult  # noqa: E402


# ─── Fake adapter ───────────────────────────────────────────────
# We script the verifier verdicts per call to drive different scenarios.

class FakeAdapter:
    def __init__(self, role_responses):
        self.role_responses = role_responses
        self.calls = []

    def query(self, prompt, system):
        # Identify role by which system prompt was passed in.
        role = self._role_from_system(system)
        self.calls.append({"role": role, "prompt": prompt})
        # Pop the next scripted response for this role; fall back to last.
        responses = self.role_responses.get(role, [])
        if not responses:
            raise AssertionError(f"No scripted response for role={role}")
        resp = responses.pop(0) if len(responses) > 1 else responses[0]
        return {
            "response": resp,
            "usage": {
                "model": "fake",
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
            },
        }

    @staticmethod
    def _role_from_system(system):
        for name, prompt in consult.ROLES.items():
            if prompt == system:
                return name
        return "unknown"


# ─── Tests ───────────────────────────────────────────────────────

class TriadModeFile(unittest.TestCase):
    def test_yaml_loads_and_has_required_shape(self):
        cfg = orchestrate.load_mode("triad")
        self.assertEqual(cfg["name"], "triad")
        steps = {s["step"]: s for s in cfg["pipeline"]}
        self.assertEqual(set(steps), {"plan", "build", "verify"})
        self.assertEqual(steps["plan"]["role"], "triad_planner")
        self.assertEqual(steps["build"]["role"], "triad_builder")
        self.assertEqual(steps["verify"]["role"], "triad_verifier")

    def test_vendor_diversity(self):
        """Roles must be assigned to three different vendors."""
        cfg = orchestrate.load_mode("triad")
        models = [s["model"] for s in cfg["pipeline"]]
        self.assertEqual(len(set(models)), 3, f"models not distinct: {models}")

    def test_max_loops_bounded(self):
        cfg = orchestrate.load_mode("triad")
        self.assertGreaterEqual(cfg["max_loops"], 1)
        self.assertLessEqual(cfg["max_loops"], 3)


class TriadRoleDiscipline(unittest.TestCase):
    """The role prompts must enforce the discipline that makes the pattern work."""

    def test_planner_forbids_writing_artifact(self):
        p = consult.ROLES["triad_planner"]
        self.assertIn("Do NOT write code", p)
        self.assertIn("plan", p.lower())

    def test_builder_forbids_redesign(self):
        p = consult.ROLES["triad_builder"]
        self.assertIn("Do NOT", p)
        self.assertIn("blocked", p)

    def test_verifier_forbids_proposing_fixes(self):
        p = consult.ROLES["triad_verifier"]
        self.assertIn("Do NOT propose fixes", p)
        for verdict in ("pass", "revise_plan", "revise_build", "reject"):
            self.assertIn(verdict, p)

    def test_verifier_reserves_full_confidence_for_pass(self):
        # The convergence check fires at confidence>=0.95, so the prompt
        # must instruct the verifier not to set 1.0 except on pass.
        p = consult.ROLES["triad_verifier"]
        self.assertIn("confidence=1.0 ONLY if verdict=pass", p)


class ConvergenceLogic(unittest.TestCase):
    def _bb(self, *responses):
        return {"consultations": [{"response": r} for r in responses]}

    def test_pass_verdict_converges(self):
        bb = self._bb({"verdict": "pass", "confidence": 1.0}, {"verdict": "pass", "confidence": 1.0})
        self.assertTrue(orchestrate.check_convergence(bb))

    def test_reject_verdict_converges(self):
        bb = self._bb({"verdict": "reject", "confidence": 0.7}, {"verdict": "reject", "confidence": 0.7})
        self.assertTrue(orchestrate.check_convergence(bb))

    def test_revise_verdict_does_not_converge(self):
        bb = self._bb({"verdict": "revise_plan", "confidence": 0.6}, {"verdict": "revise_build", "confidence": 0.5})
        self.assertFalse(orchestrate.check_convergence(bb))

    def test_high_confidence_without_verdict_still_converges(self):
        # Backward compat for non-triad modes.
        bb = self._bb({"confidence": 0.8}, {"confidence": 0.97, "analysis": "done"})
        self.assertTrue(orchestrate.check_convergence(bb))

    def test_single_consultation_does_not_converge(self):
        bb = {"consultations": [{"response": {"verdict": "pass"}}]}
        self.assertFalse(orchestrate.check_convergence(bb))


class PromptThreading(unittest.TestCase):
    """The verifier's structured fields must reach the planner on revision."""

    def test_summarizer_includes_plan(self):
        c = {
            "model": "gpt", "role": "triad_planner",
            "response": {
                "analysis": "read as refactor task",
                "plan": ["step one", "step two"],
                "confidence": 0.7,
            },
        }
        out = orchestrate._summarize_consultation(c)
        self.assertIn("plan:", out)
        self.assertIn("step one", out)
        self.assertIn("step two", out)

    def test_summarizer_includes_verdict_and_failures(self):
        c = {
            "model": "grok", "role": "triad_verifier",
            "response": {
                "analysis": "build misses requirement 2",
                "verdict": "revise_build",
                "failures": [
                    {"requirement": "must update tests", "observed": "no test changes",
                     "severity": "blocker"},
                ],
                "reasons": ["builder skipped step 4 of plan"],
                "confidence": 0.6,
            },
        }
        out = orchestrate._summarize_consultation(c)
        self.assertIn("verdict: revise_build", out)
        self.assertIn("[blocker]", out)
        self.assertIn("must update tests", out)
        self.assertIn("builder skipped step 4", out)

    def test_summarizer_handles_non_dict_response(self):
        c = {"model": "x", "role": "y", "response": "raw string"}
        out = orchestrate._summarize_consultation(c)
        self.assertIn("raw string", out)


class TriadEndToEnd(unittest.TestCase):
    """Drive the full triad pipeline with a fake adapter."""

    def _run_triad(self, role_responses, max_loops_override=None):
        cfg = orchestrate.load_mode("triad")
        if max_loops_override is not None:
            cfg["max_loops"] = max_loops_override
        bb = orchestrate.init_blackboard(cfg, "Add a retry helper to api_client.py")

        fake = FakeAdapter(role_responses)
        with patch.dict(orchestrate.ADAPTERS, {"gpt": fake, "gemini": fake, "grok": fake}):
            iteration = 0
            while iteration <= bb["max_iterations"]:
                bb["iterations"] = iteration
                for step in cfg["pipeline"]:
                    orchestrate.run_step(step, bb)
                if orchestrate.check_convergence(bb):
                    break
                iteration += 1
        return bb, fake

    def test_pass_on_first_iteration_stops_loop(self):
        bb, fake = self._run_triad({
            "triad_planner": [{"plan": ["a", "b"], "confidence": 0.8, "analysis": "p"}],
            "triad_builder": [{"implementation": "code", "plan_followed": True,
                               "blocked": False, "confidence": 0.9, "analysis": "b"}],
            "triad_verifier": [{"verdict": "pass", "confidence": 1.0,
                                "requirements_recovered": ["retry helper exists"],
                                "failures": [], "reasons": ["all met"], "analysis": "v"}],
        })
        # Three calls only — no second iteration.
        self.assertEqual(len(fake.calls), 3)
        last = bb["consultations"][-1]["response"]
        self.assertEqual(last["verdict"], "pass")

    def test_revise_plan_triggers_second_iteration(self):
        bb, fake = self._run_triad({
            "triad_planner": [
                {"plan": ["bad step"], "confidence": 0.5, "analysis": "p1"},
                {"plan": ["fixed step"], "confidence": 0.8, "analysis": "p2"},
            ],
            "triad_builder": [
                {"implementation": "code1", "plan_followed": True, "blocked": False,
                 "confidence": 0.7, "analysis": "b1"},
                {"implementation": "code2", "plan_followed": True, "blocked": False,
                 "confidence": 0.85, "analysis": "b2"},
            ],
            "triad_verifier": [
                {"verdict": "revise_plan", "confidence": 0.6,
                 "failures": [{"requirement": "X", "observed": "Y", "severity": "blocker"}],
                 "reasons": ["plan ignored constraint Z"], "analysis": "v1"},
                {"verdict": "pass", "confidence": 1.0, "failures": [],
                 "reasons": ["all met"], "analysis": "v2"},
            ],
        })
        self.assertEqual(len(fake.calls), 6)  # 3 + 3
        # Planner on second iteration must have seen verifier's first-round output.
        planner_calls = [c for c in fake.calls if c["role"] == "triad_planner"]
        self.assertEqual(len(planner_calls), 2)
        second_planner_prompt = planner_calls[1]["prompt"]
        self.assertIn("revise_plan", second_planner_prompt)
        self.assertIn("plan ignored constraint Z", second_planner_prompt)

    def test_reject_short_circuits(self):
        bb, fake = self._run_triad({
            "triad_planner": [{"plan": ["x"], "confidence": 0.4, "analysis": "p"}],
            "triad_builder": [{"implementation": "code", "plan_followed": True,
                               "blocked": False, "confidence": 0.5, "analysis": "b"}],
            "triad_verifier": [{"verdict": "reject", "confidence": 0.7,
                                "reasons": ["task infeasible"], "failures": [], "analysis": "v"}],
        })
        # Reject after first round must stop the loop.
        self.assertEqual(len(fake.calls), 3)
        self.assertEqual(bb["consultations"][-1]["response"]["verdict"], "reject")


if __name__ == "__main__":
    unittest.main(verbosity=2)
