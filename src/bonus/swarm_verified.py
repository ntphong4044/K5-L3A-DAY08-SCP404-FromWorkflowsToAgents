"""Bonus B3 — swarm_verified: the reference swarm plus a code verifier before the write.

The swarm is kept as-is (peer + parse model calls, read-only investigators, and the
seed % 5 == 0 weakness that trusts the ticket delay). The only change is a verifier
step that runs after the swarm has built its quote and before anything is decided:

  * It compares every fact the quote depends on (delay_days, status, damage_verified)
    with the structured order row returned by the investigator.
  * On a mismatch it re-quotes from the structured order (at most one correction round)
    and writes a `verifier_override` event to the trace with the field names only.
  * The verifier is code, not a model call: it cannot be talked out of the DB value.

Run next to the official shapes (from src/):
    python -m lab8.benchmark --shapes workflow,swarm,swarm_verified \
        --extra-shape swarm_verified=bonus.swarm_verified:run_claim \
        --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, tool_cost
from lab8.trace import Trace

SHAPE = "swarm_verified"
# Facts compute_compensation reads from the order. If any differs from the DB row, the quote is suspect.
VERIFIED_FIELDS = ("delay_days", "status", "damage_verified")
MAX_CORRECTIONS = 1


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def verify_quote(
    conn: sqlite3.Connection,
    budget: Budget,
    used_order: dict[str, Any],
    db_order: dict[str, Any],
    quote_payload: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Return (quote to use, mismatched field names).

    One correction round (MAX_CORRECTIONS = 1): re-quote from the DB row. The DB row is
    the source of truth, so one round always converges; no loop is needed.
    """
    mismatched = [f for f in VERIFIED_FIELDS if used_order.get(f) != db_order.get(f)]
    if mismatched:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, db_order)
    return quote_payload, mismatched


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        return finish(
            conn, shape=SHAPE, claim_id=claim_id, seed=seed, status=status,
            proposal_amount=proposal, budget=budget, trace=trace, error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", 0, "unknown_claim")

    # --- unchanged swarm behaviour: peers read the ticket ---
    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return done("needs_info", 0, "missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim_row["principal_id"])
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add("investigator", {"lookup_order": order_view})
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return done("escalated", 0, order_view.get("reason"))

    db_order = dict(order_view["order"])
    used_order = dict(db_order)
    # Same weakness as the reference swarm: one seed in five trusts the ticket delay.
    if parsed_delay is not None and parsed_delay != int(used_order["delay_days"]) and seed % 5 == 0:
        used_order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})
    quote_payload = investigated["tools"]["compute_compensation"]
    if used_order != db_order:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, used_order)

    # --- B3: code verifier between the swarm's quote and any decision ---
    quote_payload, mismatched = verify_quote(conn, budget, used_order, db_order, quote_payload)
    if mismatched:
        trace.add("verifier_override", {"fields": mismatched, "requoted_from": "order_row"})
    else:
        trace.add("verifier_ok", {"fields_checked": list(VERIFIED_FIELDS)})

    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return done("denied", 0, quote_payload.get("reason"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal, None)
