# Team

## Thông tin nhóm

- Tên nhóm: SCP404
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-SCP404-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/ntphong4044/K5-L3A-DAY08-SCP404-FromWorkflowsToAgents, nhánh main, aba170e

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Tuấn Phong | 2A202603712 | nt.phong.forwork@gmail.com | ntphong4044 | Shape A Workflow, Integration |
|   2 | Lê Anh Quân | 2A202603576 | leanhquan111555999@gmail.com| quanle28 | Shape B Single (ReAct) |
|   3 | Kim Đức Thắng | 2A202603702 | thangtobeo141@gmail.com | thangbeo141 | Shape C Orchestrator, Handoff |
|   4 | Trần Đức Mạnh | 2A202603615 | trmanh204@gmail.com | trmanh204 | Shape D Swarm, Crash Suite, Eval & ADR |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Tuấn Phong | Shape A Workflow, Integration | cb097ad, aa781c9 | src/tests/test_workflow_safety.py |
| Lê Anh Quân | Shape B Single (ReAct) | 0e28b4e | src/tests/test_single_safety.py |
| Kim Đức Thắng | Shape C Orchestrator, Handoff | 927f00b | src/tests/test_orchestrator_safety.py |
| Trần Đức Mạnh | Shape D Swarm, Crash Suite, Eval & ADR | aba170e, 3f9126a | src/tests/test_manh_eval.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Tóm tắt từng thành viên bên dưới; chi tiết trong báo cáo cá nhân tương ứng.

### 1. 2A202603712_NguyenTuanPhong — Nguyễn Tuấn Phong

**Phần việc phụ trách**

- Shape A `workflow` (`src/lab8/shapes/workflow.py`): claims flow bằng các bước Python cố định (CP2, CP3).
- Tích hợp nhóm: merge code các thành viên, giữ `python -m pytest -q` xanh, điền `TEAM.md`.

**Đóng góp cụ thể**

- Thay stub `not_implemented` bằng workflow: `get_claim_view` → `needs_info` khi thiếu `order_id` → `lookup_order` theo principal (`escalated` khi không thấy) → quote bằng `compute_compensation` từ order row → `denied` khi quote 0 → `issue_refund` với quote đầy đủ và `crash_at`. MockLLM chỉ soạn câu trả lời.
- Không bắt `InjectedCrash` (flush trace rồi ném lại); trace không ghi ticket, claim row hay order row thô.
- Test `src/tests/test_workflow_safety.py` (5 test): ticket khai trễ sai (C-002, cả 5 seed), prompt injection (C-009), `needs_info` vẫn có trace, không lộ secret/PII, crash rồi resume chỉ một refund.

**Bằng chứng**

- Commit: `cb097ad` (workflow), `aa781c9` (test).
- `pytest -m student -k "workflow]"`: 62 passed; `tests/test_workflow_safety.py`: 5 passed.
- Báo cáo cá nhân: `report/team/2A202603712_NguyenTuanPhong.md`

### 2. 2A202603576_LeAnhQuan — Lê Anh Quân

**Phần việc phụ trách**

- Shape B `single` (`src/lab8/shapes/single.py`): một agent ReAct qua `run_react`, `max_steps=8`.
- Rà các nhánh approval (hết hạn, bị thu hồi, thuộc claim khác, đơn đã hoàn đủ) trên cả ba shape.

**Đóng góp cụ thể**

- `decide()` chỉ chọn tool đọc (`lookup_order`, `lookup_policy`, `lookup_refund_history`), chạy với `worker=True` để runtime từ chối tool ghi; mỗi lượt quyết định tính một model call vào `Budget`.
- Sau vòng lặp, code quote từ order view đã kiểm principal và gọi `issue_refund` với quote đầy đủ; host từ chối → `denied`, xung đột số tiền → `failed`.
- Test `src/tests/test_single_safety.py` (8 ca): chỉ dispatch tool đọc, ticket khai trễ 99 ngày và dẫn clause cũ, trả về sớm có trace, hết step cap, policy bị thay thế/chưa hiệu lực, xung đột số tiền.

**Bằng chứng**

- Commit: `0e28b4e`.
- `pytest -m student -k "single]"`: 62 passed; `test_single_safety.py` + test approval của host: 19 passed.
- Báo cáo cá nhân: `report/team/2A202603576_LeAnhQuan.md`

### 3. 2A202603702_KimDucThang — Kim Đức Thắng

**Phần việc phụ trách**

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`) với investigator chỉ đọc.
- Ranh giới bảo mật handoff và trace (C5); durability CP3 (`crash_at`, `InjectedCrash`).

**Đóng góp cụ thể**

- Handoff dựng bằng `make_handoff` theo allowlist, chỉ cấp tool đọc (`lookup_order`, `lookup_policy`, `compute_compensation`); trace ghi handoff đã sanitize, không ghi parent context.
- Orchestrator quote từ order view của investigator và là nơi duy nhất gọi `issue_refund` với quote đầy đủ.
- Test `src/tests/test_orchestrator_safety.py` (3 test): canary trong `parent_secret` không lọt trace, đơn ngoài phạm vi `escalated` không lộ PII, crash rồi resume không ghi trùng.

**Bằng chứng**

- Commit: `927f00b`.
- `pytest -m student -k "orchestrator]"`: 62 passed; `test_handoff_secret.py` + `test_orchestrator_safety.py`: 6 passed.
- Báo cáo cá nhân: `report/team/2A202603702_KimDucThang.md`

### 4. 2A202603615_TranDucManh — Trần Đức Mạnh

**Phần việc phụ trách**

- Shape D `swarm` (đối chứng): phân tích nguyên nhân fail ở seed 55.
- CP4: crash suite. CP5: benchmark 4 shape × 14 claim × 5 seed, ADR, research card, `check_submission`.

**Đóng góp cụ thể**

- Phân tích swarm: khi `seed % 5 == 0`, swarm tin số ngày trễ trong ticket thay vì order row; C-002 (ticket 5 ngày, DB 2 ngày) bị `resolved` thay vì `denied`.
- Sinh `src/reports/crash.json` và `src/reports/benchmark.json`; viết `report/team/decision_adr.md` (chọn workflow) và `report/team/research_card.md` (R2, MAST).
- Test `src/tests/test_manh_eval.py` (2 test): swarm xác định với cùng seed; swarm pass C-002 ở seed 11 nhưng fail ở seed 55.

**Bằng chứng**

- Commit: `aba170e` (reports, test), `3f9126a` (ADR, research card).
- `crash_safety` 20/20; benchmark: workflow pass rate 1.0, cost/success 28.8 VND; swarm pass rate 0.986, pass^5 0.929.
- Run id: `R-workflow-C-001-s11`, `R-swarm-C-002-s55`.
- Báo cáo cá nhân: `report/team/2A202603615_TranDucManh.md`

