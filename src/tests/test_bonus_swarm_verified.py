"""B3 — swarm_verified. Run from src/: python -m pytest -q tests/test_bonus_swarm_verified.py"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bonus import swarm_verified
from lab8.benchmark import run_benchmark
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash
from lab8.shapes import SHAPES, swarm_reference

BONUS_DIR = Path(__file__).resolve().parents[1] / "bonus"
B_WORLD = load_json(BONUS_DIR / "world.json")
B_CASES = load_jsonl(BONUS_DIR / "cases.jsonl")
SEEDS = [11, 22, 33, 44, 55]


@pytest.fixture
def bonus_db(tmp_path: Path) -> Path:
    store = tmp_path / "bonus.sqlite"
    init_store(store, B_WORLD, B_CASES).close()
    return store


def _events(result) -> list[dict]:
    return json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]


def _kinds(result) -> list[str]:
    return [e["kind"] for e in _events(result)]


def test_verifier_fixes_swarm_t02_failure_on_seed_55(public_db):
    """Public C-002: ticket 5 days, DB 2. Reference swarm pays at seed 55; verified swarm denies."""
    swarm = swarm_reference.run_claim("C-002", seed=55, store_path=str(public_db))
    assert swarm.status == "resolved"  # the known reference weakness

    conn = connect(public_db)
    try:
        conn.execute("DELETE FROM refund_ledger WHERE claim_id = 'C-002'")
        conn.execute("DELETE FROM audit_events WHERE claim_id = 'C-002'")
        conn.commit()
    finally:
        conn.close()

    verified = swarm_verified.run_claim("C-002", seed=55, store_path=str(public_db))
    assert verified.status == "denied"
    assert verified.proposal_amount == 0
    assert verified.refund_effects == []
    kinds = _kinds(verified)
    assert kinds.index("model_override") < kinds.index("verifier_override") < kinds.index("quote")


def test_verifier_restores_understated_delay(bonus_db):
    """B-02: ticket says 1 day, DB 5 -> swarm alone denies at seed 55; verifier re-quotes and pays."""
    result = swarm_verified.run_claim("B-02", seed=55, store_path=str(bonus_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 30000
    assert [e["amount_vnd"] for e in result.refund_effects] == [30000]


def test_verifier_silent_when_facts_match(bonus_db):
    """B-09: ticket delay equals DB delay -> no override, one verifier_ok event."""
    result = swarm_verified.run_claim("B-09", seed=55, store_path=str(bonus_db))
    kinds = _kinds(result)
    assert "verifier_override" not in kinds and "model_override" not in kinds
    assert kinds.count("verifier_ok") == 1
    assert result.status == "resolved"


def test_order_cap_still_enforced_after_verifier(bonus_db):
    """B-10: DB 4 days but order already refunded in full -> full quote to host, host denies."""
    result = swarm_verified.run_claim("B-10", seed=55, store_path=str(bonus_db))
    assert result.status == "denied"
    assert result.proposal_amount == 30000
    assert result.error_reason == "order_already_refunded"


def test_crash_after_effect_then_resume_single_refund(bonus_db):
    with pytest.raises(InjectedCrash):
        swarm_verified.run_claim("B-02", seed=55, store_path=str(bonus_db), crash_at="after_effect_before_checkpoint")
    resumed = swarm_verified.run_claim("B-02", seed=55, store_path=str(bonus_db))
    assert resumed.status == "resolved"
    assert resumed.committed_audit_count == 1
    conn = connect(bonus_db)
    try:
        assert conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'B-02'").fetchone()["n"] == 1
    finally:
        conn.close()


def test_trace_has_no_secret_or_pii(bonus_db):
    for case in B_CASES:
        conn = connect(bonus_db)
        try:
            conn.execute("DELETE FROM refund_ledger WHERE claim_id = ?", (case["claim_id"],))
            conn.commit()
        finally:
            conn.close()
        result = swarm_verified.run_claim(case["claim_id"], seed=55, store_path=str(bonus_db))
        text = Path(result.trace_path).read_text(encoding="utf-8")
        for token in case["expected"]["forbid_substrings"]:
            assert token not in text


def test_adversarial_labels_and_verified_swarm_pass_all(monkeypatch):
    """Hand labels agree with workflow (which never reads the ticket); swarm_verified passes every trial."""
    monkeypatch.setitem(SHAPES, "swarm_verified", swarm_verified.run_claim)
    report = run_benchmark(world=B_WORLD, claims=B_CASES, shapes=["workflow", "swarm", "swarm_verified"], seeds=SEEDS)
    stats = report["by_shape"]
    assert stats["workflow"]["pass_rate"] == 1.0
    assert stats["swarm_verified"]["pass_rate"] == 1.0
    assert stats["swarm_verified"]["seed_variance"] == 0.0
    assert stats["swarm"]["pass_rate"] < 1.0
    failed = sorted(t["claim_id"] for t in report["trials"] if t["shape"] == "swarm" and not t["passed"])
    assert failed == ["B-01", "B-02", "B-07", "B-08", "B-10"]
    assert all(t["seed"] == 55 for t in report["trials"] if t["shape"] == "swarm" and not t["passed"])
