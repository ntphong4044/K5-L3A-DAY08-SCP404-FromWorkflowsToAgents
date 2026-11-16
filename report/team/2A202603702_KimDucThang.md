# Báo cáo cá nhân — 2A202603702_KimDucThang

## 1. Thông tin thành viên

- Họ tên: Kim Đức Thắng
- MSSV: 2A202603702
- Email: thangtobeo141@gmail.com
- GitHub: thangbeo141

## 2. Phần việc phụ trách

- Phụ trách nghiên cứu và hiện thực **Shape C — Orchestrator** (`src/lab8/shapes/orchestrator.py`) phối hợp với các read-only investigators.
- Thiết kế cơ chế phân tách quyền hạn (Privilege Separation) và **Typed Handoff** an toàn qua `lab8.handoff.make_handoff`, chỉ cấp quyền truy cập các read-only tools (`lookup_order`, `lookup_policy`, `compute_compensation`).
- Đảm bảo ranh giới bảo mật (tiêu chí chấm C5): Ngăn chặn rò rỉ thông tin nhạy cảm (`parent_secret`, `raw_headers`, canary tokens) và thông tin định danh cá nhân (PII: số điện thoại, địa chỉ, ghi chú nội bộ, tên mặt hàng) qua handoff và trace.
- Hiện thực tính bền vững và khả năng chịu lỗi (CP3 - Durability & Crash Safety): Truyền tham số `crash_at` vào `durability.issue_refund`, ghi nhận trace và để ngoại lệ `InjectedCrash` lan truyền đúng chuẩn, hỗ trợ resume sau sự cố mà không ghi trùng tiền (Idempotency).

## 3. Đóng góp cụ thể

- **Cài đặt Shape C Orchestrator:**
  - Hoàn thiện hàm `run_claim` và `_run` trong `src/lab8/shapes/orchestrator.py` tuân thủ đúng Output Contract và Trace Contract v1.
  - Xử lý phân nhánh logic:
    - Kiểm tra claim view qua allowlist; nếu thiếu `order_id` trả về `needs_info`, không tự đoán mã đơn từ nội dung ticket.
    - Đóng gói handoff được khử khuẩn (`sanitize`) và điều phối điều tra qua `run_readonly_investigators`.
    - Kiểm tra quyền sở hữu đơn hàng (`visible`); nếu khách không sở hữu đơn lập tức trả `escalated` mà không để lộ PII.
    - Lấy báo giá bồi hoàn (`compute_compensation`); nếu quote $\le 0$ trả `denied` mà không gọi host writer.
    - Truyền toàn bộ số tiền bồi hoàn gốc (`full quote`) vào `issue_refund` để host tự xử lý trần hoàn tiền theo đơn và khấu trừ khoản đã hoàn trước đó (tránh lỗi trừ 2 lần ở T13, T14).
- **Quyết định kỹ thuật:**
  - Áp dụng nguyên tắc Allowlist tuyệt đối thay vì dùng LLM để tóm tắt (vì tóm tắt bằng LLM không đảm bảo loại bỏ hoàn toàn secret).
  - Tách bạch hoàn toàn ranh giới giữa Worker (chỉ đọc) và Host/Orchestrator (ghi ledger).
  - Sử dụng hàm chuẩn `lab8.shapes.common.finish()` để tạo `RunResult`, tự động đồng bộ audit log và ledger SQLite.
- **Xây dựng bộ kiểm thử an toàn:**
  - Tạo file kiểm thử mới `src/tests/test_orchestrator_safety.py` gồm 3 bài test độc lập:
    1. `test_orchestrator_handoff_drops_parent_secret_and_canary`: Kiểm tra tiêm canary secret và xác minh trace không chứa secret.
    2. `test_orchestrator_read_only_tools_and_escalation_on_unauthorized_order`: Kiểm tra trường hợp đơn không thuộc quyền sở hữu (C-005) được chuyển tiếp `escalated` an toàn, không rò rỉ PII.
    3. `test_orchestrator_idempotent_retry_and_crash_propagation`: Kiểm chứng ngoại lệ `InjectedCrash` văng ra chính xác và khôi phục sau crash không tạo bản ghi trùng lặp.

## 4. Bằng chứng

- **Commit hash:** `927f00b` (`add orchestrator shape and safety regression tests`)
- **File kiểm thử:** `src/tests/test_orchestrator_safety.py` (3/3 passed)
- **Kết quả kiểm thử:**
  - Ma trận kiểm thử riêng Shape C: `pytest -q -m student -o addopts= -k orchestrator` đạt **62/62 passed** (100% xanh, bao gồm T11 idempotent retry và T12 crash recovery).
  - Kiểm thử bảo mật handoff: `pytest -q tests/test_handoff_secret.py tests/test_orchestrator_safety.py` đạt **6/6 passed**.
  - Kiểm thử toàn hệ thống: `pytest -q -m student -o addopts=` đạt **248/248 passed** trên cả 4 kiến trúc.
  - Lệnh nghiệm thu: `python -m lab8.check_submission` đạt **0 FAIL**.
- **Run ID dẫn chứng:**
  - `R-orchestrator-C-001-s11` (Resolved chuẩn, hoàn phí ship 35.000 VNĐ)
  - `R-orchestrator-C-005-s11` (Escalated chuẩn, không rò rỉ PII)
  - `R-orchestrator-C-010-s11` (Resolved chuẩn, trace sạch hoàn toàn không chứa canary token)

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity Assistant.
- **Mục đích sử dụng:**
  - Hỗ trợ đối chiếu các ràng buộc trong Trace Contract v1 và Output Contract.
  - Đề xuất các trường hợp biên (edge cases) và cấu trúc bài test kiểm tra rò rỉ canary secret trong handoff.
- **Phương pháp tự kiểm tra:**
  - Trực tiếp rà soát từng dòng code trong `src/lab8/shapes/orchestrator.py` để đảm bảo không gọi tool ghi trái phép.
  - Chạy thực nghiệm toàn bộ test suite cục bộ qua `pytest` trong môi trường ảo `.venv`.
  - Mở trực tiếp các file trace JSON được sinh ra trong thư mục `src/traces/` để quét chuỗi thủ công, đảm bảo tuyệt đối không có `CANARY_SECRET_`, header hay thông tin nhạy cảm nào bị ghi vào nhật ký.

## 6. Tự đánh giá

- Hoàn thành đầy đủ và vượt tiến độ toàn bộ các yêu cầu của Checkpoint 2 (CP2) và Checkpoint 3 (CP3) cho Shape C.
- Đạt điểm tối đa ở tiêu chí bảo mật ranh giới handoff (C5) và tiêu chí đóng góp cá nhân có commit/test thực tế (C8).
- Phối hợp chặt chẽ với các thành viên khác trong nhóm (TV1, TV2, TV4) để đảm bảo toàn bộ hệ thống vận hành thống nhất, không có xung đột mã nguồn.
