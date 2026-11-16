# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: SCP404
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 61b422a

## 2. Mục tiêu và cách tiếp cận

Bài toán yêu cầu xử lý quy trình yêu cầu bồi thường (claims) cước vận chuyển và hàng hư hỏng cho công ty giả lập LogiX-VN trên 4 hình thái kiến trúc có mức độ tự chủ tăng dần: Workflow (A), Single ReAct Agent (B), Orchestrator + Sub-agents (C), và Swarm (D).
Nhóm tiếp cận theo nguyên tắc:
1. **Host-driven Authority:** Toàn bộ ranh giới tài chính, chính sách bảo hiểm, hạn mức bồi thường theo đơn và tính không lặp lại (idempotency ledger) do tầng Host kiểm soát. Mô hình AI chỉ hỗ trợ đọc hiểu dữ liệu và soạn văn bản, tuyệt đối không tự tính tiền bồi hoàn.
2. **Sanitization & Security:** Handoff giữa Orchestrator và Investigator tuân thủ allowlist nghiêm ngặt, loại bỏ hoàn toàn các trường dữ liệu nhạy cảm (`CANARY_SECRET_*`, PII).
3. **Thực nghiệm định lượng:** Đánh giá các kiến trúc dựa trên 4 chỉ số cốt lõi: Pass rate, Pass^5, Phương sai (Seed variance), và Chi phí hiệu dụng (Cost per success).

## 3. Giải pháp

- **Shape A (Workflow):** Cài đặt luồng thực thi tuần tự hoàn toàn bằng code Python xác định. Đọc thông tin qua view `get_claim_view`, kiểm tra điều kiện đơn hàng qua `lookup_order`, tính tiền bằng `compute_compensation`, và gọi cổng host `durability.issue_refund` với đầy đủ báo giá (quote).
- **Shape B (Single Agent):** Ứng dụng vòng lặp suy luận ReAct với giới hạn tối đa 8 bước đọc. Agent chỉ được cấp quyền sử dụng các công cụ chỉ đọc (`lookup_order`, `lookup_policy`, `lookup_refund_history`), không có quyền ghi. Sau khi vòng lặp dừng, code của shape mới gọi host ghi sổ cái.
- **Shape C (Orchestrator):** Điều phối viên phân tách nhiệm vụ và tạo gói bàn giao `make_handoff` được khử khuẩn cho các Investigator chỉ đọc. Investigator chỉ trả về góc nhìn dữ liệu (order view, policy view), Orchestrator tổng hợp và gọi host thực thi ghi refund.
- **Shape D (Swarm):** Hệ đa tác tử cộng tác ngang hàng, được dùng làm baseline đối chứng về chi phí và phương sai.

## 4. Kết quả

Số liệu trích xuất từ `src/reports/benchmark.json` (chạy trên 14 claims $\times$ 5 seeds = 70 trials):

| Shape | Pass Rate | Pass^5 | Seed Min - Max | Variance | Cost/Success (VND) | Mean Steps |
|---|---:|---:|---:|---:|---:|---:|
| **Workflow (A)** | **1.000** | **1.000** | **1.000 - 1.000** | **0.000000** | **28.80** | **4.43** |
| **Single (B)** | 1.000 | 1.000 | 1.000 - 1.000 | 0.000000 | 47.22 | 8.64 |
| **Orchestrator (C)** | 1.000 | 1.000 | 1.000 - 1.000 | 0.000000 | 47.37 | 5.36 |
| **Swarm (D)** | 0.986 | 0.929 | 0.929 - 1.000 | 0.000816 | 49.57 | 2.80 |

- **Crash Safety:** Đạt điểm tuyệt đối **`20/20`** theo báo cáo [src/reports/crash.json](../../src/reports/crash.json), đảm bảo tính an toàn giao dịch khi xảy ra sự cố sập nguồn/crash ở mọi thời điểm.
- **Quyết định kiến trúc:** Nhóm lựa chọn **Shape A (Workflow)** làm kiến trúc tối ưu để nộp bài đánh giá cổng hidden. Chi tiết lập luận nằm tại [report/team/decision_adr.md](decision_adr.md).
- **Nghiên cứu nguyên nhân thất bại (Ablation):** Chi tiết phân tích nguyên nhân thất bại của Swarm tại seed 55 nằm tại [report/team/research_card.md](research_card.md).
- **Bonus B3 (verifier cho swarm):** thêm một bước kiểm tra bằng code trước khi ghi tiền. Trên bộ public, `swarm_verified` đạt pass rate 1.000, pass^5 1.000 (swarm gốc 0.986 / 0.929); trên 10 claim đối kháng tự viết, 1.000 / 1.000 so với 0.900 / 0.500 của swarm, chi phí thêm 1 tool call mỗi lần verifier can thiệp. Số liệu: `src/reports/bonus_b3_summary.json`; phân tích: [report/team/bonus_report.md](bonus_report.md).

## 5. Khó khăn và cách xử lý

1. **Ranh giới tính tiền giữa Host và Shape:** Ban đầu dễ mắc bẫy tự trừ tiền đã hoàn của đơn hàng trước đó trước khi gọi `issue_refund`. Nhóm đã đọc kỹ luật nghiệp vụ và sửa lại: Shape luôn truyền quote đầy đủ, để Host tự động trừ phần chênh lệch nhằm tránh trừ lặp lại 2 lần (đặc biệt ở claim T14).
2. **Rò rỉ dữ liệu qua Handoff:** Trong Orchestrator, cần lọc bỏ toàn bộ thông tin nhạy cảm của khách hàng bằng cách áp dụng allowlist nghiêm ngặt trong `make_handoff` và chỉ cấp các tool đọc.
3. **Đồng bộ mã nguồn nhóm:** Sử dụng Git phân nhánh và commit độc lập, tránh xung đột trên các file mã nguồn của từng shape.

## 6. Tổng hợp đóng góp

- **Nguyễn Tuấn Phong:** Hiện thực Shape A (`workflow.py`), bộ test `test_workflow_safety.py`, tích hợp nhóm, bonus B3 (`src/bonus/`, `test_bonus_swarm_verified.py`).
- **Lê Anh Quân:** Hiện thực Shape B (`single.py`), bộ test `test_single_safety.py`.
- **Kim Đức Thắng:** Hiện thực Shape C (`orchestrator.py`), bộ test `test_orchestrator_safety.py`.
- **Trần Đức Mạnh:** Nghiên cứu Swarm, thực thi Crash Suite (`crash.json`), chạy Benchmark (`benchmark.json`), viết test `test_manh_eval.py`, hoàn thiện ADR, Research Card và nghiệm thu.

## 7. Hạn chế và hướng cải thiện

- MockLLM trong bài lab là mô hình mô phỏng với các bẫy ngữ cảnh xác định theo seed, chưa phản ánh đầy đủ độ trễ mạng và tính bất định của các mô hình thương mại lớn (như GPT-4 hay Gemini Pro).
- Hướng cải thiện: Khi mở rộng sang xử lý văn bản phức tạp, phi cấu trúc (như hóa đơn viết tay hoặc hợp đồng đa phương), có thể cân nhắc tích hợp Single Agent có kiểm chứng hoặc Orchestrator đa tác tử với chốt chặn an toàn (Guardrails) của Host.

## 8. Tài liệu tham khảo

1. Google Research (2026), *Towards a Science of Scaling Agent Systems*.
2. MAST, NeurIPS (2025), *Why Do Multi-Agent LLM Systems Fail?*.
3. AgentArch, AACL (2026), *Evaluating Topology Trade-offs in LLM Agent Workflows*.
