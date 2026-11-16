# Team

## Thông tin nhóm

- Tên nhóm: SCP404
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-SCP404-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/ntphong4044/K5-L3A-DAY08-SCP404-FromWorkflowsToAgents, nhánh main, aba170e

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Tuấn Phong | 20210001 | phong.nt@example.com | ntphong404 | Shape A Workflow, Integration |
|   2 | Lê Anh Quân | 20210002 | quan.la@example.com | quanle28 | Shape B Single (ReAct) |
|   3 | Kim Đức Thắng | 20210003 | thang.kd@example.com | thangbeo141 | Shape C Orchestrator, Handoff |
|   4 | Trần Đức Mạnh | 20210004 | trmanh204@gmail.com | trmanh204 | Shape D Swarm, Crash Suite, Eval & ADR |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Tuấn Phong | Shape A Workflow | cb097ad | test_workflow_safety.py |
| Lê Anh Quân | Shape B Single (ReAct) | 0e28b4e | test_single_safety.py |
| Kim Đức Thắng | Shape C Orchestrator | 927f00b | test_orchestrator_safety.py |
| Trần Đức Mạnh | Shape D Swarm & Eval/ADR | aa781c9 | test_manh_eval.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 20210004_TranDucManh

### Phần việc phụ trách

- Nghiên cứu cơ chế hoạt động của Shape D (Swarm Reference), phân tích nguyên nhân phương sai tại seed 55.
- Thực thi kiểm thử Crash Suite (20 kịch bản deterministic crash points) đạt độ an toàn 20/20.
- Vận hành Benchmark 4 kiến trúc trên 5 seed công khai và phân tích dữ liệu so sánh.
- Viết hồ sơ quyết định kiến trúc (Decision ADR), Research Card R2 và báo cáo nghiệm thu nộp bài.

### Đóng góp cụ thể

- Thêm bộ kiểm thử độc lập `src/tests/test_manh_eval.py` kiểm chứng tính nhất quán và phương sai của Swarm.
- Hoàn thiện tài liệu `report/team/decision_adr.md` và `report/team/research_card.md`.
