# Báo cáo cá nhân — 20210004_TranDucManh

## 1. Thông tin thành viên

- Họ tên: Trần Đức Mạnh
- MSSV: 20210004
- Email: trmanh204@gmail.com
- GitHub: trmanh204

## 2. Phần việc phụ trách

- Phụ trách nghiên cứu và đối chứng Shape D (Swarm Reference).
- Phụ trách đo lường độ bền vững (Durability / Idempotency / Crash safety) bằng Crash Test Suite.
- Vận hành Benchmark tổng thể trên 4 kiến trúc (Workflow, Single, Orchestrator, Swarm) và 5 seed công khai.
- Chịu trách nhiệm chính xây dựng hồ sơ quyết định kiến trúc (`report/team/decision_adr.md`) và phiếu nghiên cứu (`report/team/research_card.md`).

## 3. Đóng góp cụ thể

- Phân tích cơ chế suy diễn của Swarm và lý giải nguyên nhân sai lệch tại `seed % 5 == 0` (seed 55) do tin vào thông tin ticket thay vì order DB.
- Thêm bài kiểm thử độc lập `src/tests/test_manh_eval.py` kiểm chứng tính xác định (determinism) và phương sai seed của Swarm.
- Chạy và ghi nhận bộ kịch bản Crash Test Suite 20/20 điểm an toàn trong `src/reports/crash.json`.
- Trích xuất dữ liệu đo lường định lượng từ `src/reports/benchmark.json`, bảo vệ quyết định lựa chọn Shape A (Workflow) là kiến trúc tối ưu.

## 4. Bằng chứng

- Commit hash: `aa781c9`
- File kiểm thử: `src/tests/test_manh_eval.py` (2 passed)
- Báo cáo crash an toàn: `src/reports/crash.json` (`crash_safety: 20/20`)
- Báo cáo benchmark: `src/reports/benchmark.json` (Run id dẫn chứng: `R-workflow-C-001-s11`)

## 5. Công cụ AI đã dùng

- Công cụ: Antigravity Assistant.
- Mục đích sử dụng: Hỗ trợ phân tích luật nghiệp vụ, gợi ý cấu trúc bài test và định dạng các bảng báo cáo ADR theo đúng quy định rubric.
- Phương pháp tự kiểm tra: Chạy thực tế toàn bộ test suite qua `pytest`, đối chiếu nghiêm ngặt kết quả JSON từ các công cụ `crash_test` và `benchmark` với rubric chấm điểm, đảm bảo không sửa tay bất kỳ số liệu nào.

## 6. Tự đánh giá

- Hoàn thành xuất sắc toàn bộ các mục tiêu của CP4 (Must-pass) và CP5 (Benchmark & ADR).
- Phối hợp hiệu quả với các thành viên trong nhóm, bảo đảm mã nguồn và tài liệu đồng bộ, đạt chuẩn nghiệm thu `check_submission`.
