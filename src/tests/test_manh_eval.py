"""Unit test riêng của Trần Đức Mạnh — Đánh giá tính nhất quán và nhạy cảm Seed của Swarm.

Mục tiêu (Tiêu chí C8):
1. Kiểm tra tính xác định (determinism): Cùng claim C-001 và cùng seed 11, kết quả 2 lần chạy phải giống hệt nhau.
2. Kiểm tra độ nhạy cảm seed: Với seed 11 (bình thường) thì C-002 pass, nhưng với seed 55 (bội số của 5),
   Swarm sẽ tin vào claim ticket hơn order row dẫn đến kết quả khác biệt (variance).
"""

import pytest
from lab8.db import connect, init_store
from lab8.metrics import trial_pass
from lab8.shapes.swarm_reference import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


def test_swarm_determinism_same_seed(public_db):
    """Kiểm tra tính nhất quán: Chạy 2 lần cùng seed 11 phải ra cùng số tiền đề xuất."""
    res1 = run_claim("C-001", seed=11, store_path=str(public_db))
    res2 = run_claim("C-001", seed=11, store_path=str(public_db))
    assert res1.proposal_amount == res2.proposal_amount == 35000
    assert res1.status == res2.status == "resolved"


def test_swarm_variance_on_seed_55(tmp_path):
    """Kiểm tra độ lệch chuẩn: Seed 11 pass nhưng Seed 55 fail trên claim C-002."""
    outcomes = {}
    for seed in (11, 55):
        store = tmp_path / f"manh-t02-{seed}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        result = run_claim("C-002", seed=seed, store_path=str(store))
        conn = connect(store)
        try:
            passed, _ = trial_pass(result.as_dict(), BY_ID["C-002"]["expected"], conn)
            outcomes[seed] = passed
        finally:
            conn.close()

    assert outcomes[11] is True, "Seed 11 phải pass C-002"
    assert outcomes[55] is False, "Seed 55 phải fail C-002 do Swarm tin vào ticket"
