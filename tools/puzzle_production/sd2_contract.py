"""SD2-A v1 wire constants and pure serialization; the 0.3 freeze stays intact."""
from __future__ import annotations

import time

from .analysis_contract import AnalysisBudget as LegacyBudget, apply_changes, combined_changes
from .contract import InvalidInput, digest, exact_keys

ANALYZER = "picross-sd2-analyzer-1"
RULES = "sd2-rules-1"
TRACE = "picross-sd2-trace-v1"
REPORT = "picross-sd2-report-v1"
BYTE_LIMIT = 64 * 1024 * 1024
RULE_IDS = ("E0-empty", "E0-packed", "E0-cleanup", "E1-overlap",
            "E1-exclusion", "E1-anchored", "E2-combination", "E3-support")
REASONS = ("time_limit", "work_limit", "rule_work_limit", "wave_limit",
           "trace_byte_limit", "cancelled", "memory_limit")


class AnalysisBudget(LegacyBudget):
    def __init__(self, seconds=120, *args, **kwargs):
        if type(seconds) not in (int, float):
            raise InvalidInput("Seconds must be a finite nonnegative number")
        super().__init__(seconds, *args, **kwargs)
        self.started = False

    def check(self):
        if not self.started:
            self.deadline = time.monotonic() + self.seconds
            self.started = True
        super().check()


def parameters(value=None):
    expected = {"profile": "sd2-raw-profiles-1"}
    if value is not None:
        exact_keys(value, set(expected))
        if value != expected:
            raise InvalidInput("Unknown SD2 measurement profile")
    return expected


def analysis_input(puzzle):
    return {"format": "picross-sd2-input-v1", "logic": puzzle.to_wire()}


def header(puzzle, config=None):
    return {"format": TRACE, "analysis_hash": digest(analysis_input(puzzle)),
            "analyzer": ANALYZER, "rules": RULES, "parameters": parameters(config)}


def line_event(axis, index, domains, deductions):
    rules = []
    for name in RULE_IDS:
        if name not in deductions:
            continue
        changes = [{"offset": p, "before": old, "after": new}
                   for p, (old, new) in enumerate(zip(domains, deductions[name])) if old != new]
        if changes:
            rules.append({"rule": name, "changes": changes})
    return {"axis": axis, "index": index, "rules": rules}


def result_data(puzzle, trace, r4=None, budget=None):
    from .sd2_profiles import profiles
    status = trace["status"]
    return {"analysis_hash": trace["analysis_hash"], "analyzer": ANALYZER, "rules": RULES,
            "parameters": trace["parameters"], "trace_hash": digest(trace), "status": status,
            "reason": trace["reason"], "line_analysis_complete": status == "solved",
            "line_fixpoint_confirmed": status in ("solved", "stalled"),
            "deduction_complete": status == "solved" or bool(r4 and r4["proof_status"] == "solved"),
            "profiles": profiles(puzzle, trace, budget), "r4": r4,
            "method": None, "level": None, "confidence": None, "estimated_minutes": None,
            "explanation": f"SD2-Linienanalyse {status}; drei unkalibrierte Rohprofile. "
                           "Such- und Abschnittsproxies sind keine menschlichen Zeit- oder Klickmessungen. "
                           "Keine Endnote; Kalibrierung und Integration bleiben SD2-B/C/D."}
