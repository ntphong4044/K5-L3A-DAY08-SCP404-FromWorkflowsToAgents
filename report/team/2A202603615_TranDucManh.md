# Báo cáo cá nhân — 2A202603615_TranDucManh

## 1. Thông tin thành viên

- Họ tên: Trần Đức Mạnh
- MSSV: 2A202603615
- Email: trmanh204@gmail.com
- GitHub: [trmanh204](https://github.com/trmanh204)
- Vai trò: Shape D Swarm, Đo lường (Durability & Benchmark), Quyết định kiến trúc (ADR) và Kiểm thử nghiệm thu (Check Submission).

---

## 2. Phần việc phụ trách

Trong dự án Lab 8 (LogiX-VN), tôi đảm nhận vai trò kỹ sư đo lường, đánh giá hệ thống và kiến trúc sư giải pháp (Lead Evaluator & System Architect):

1. **Phân tích đối chứng Shape D — Swarm Reference:** 
   - Khảo sát mã nguồn tham chiếu [src/lab8/shapes/swarm_reference.py](file:///d:/LAB08/K5-L3A-DAY08-SCP404-FromWorkflowsToAgents/src/lab8/shapes/swarm_reference.py).
   - Làm rõ cơ chế cộng tác ngang hàng (peer-to-peer model calling), phân tích bản chất mô phỏng của `MockLLM` và nguyên nhân gây ra phương sai thất bại ở các seed đặc thù (`seed % 5 == 0`).
2. **Đo lường độ bền vững và khả năng chịu lỗi (Durability & Crash Safety - CP3/CP4):**
   - Vận hành bộ kiểm thử độc lập `lab8.crash_test` gồm 20 kịch bản sự cố xác định (*deterministic crash points*).
   - Kiểm chứng tính bất biến của sổ cái (Idempotency Ledger): Đảm bảo khi hệ thống gặp sự cố mất điện/sập nguồn (`InjectedCrash`) ở bất kỳ mắt xích nào trước hoặc sau checkpoint, quá trình phục hồi lại (`resume`) tuyệt đối không tạo ra nhiều hơn 1 khoản hoàn tiền (`crash_safety = 20/20`).
3. **Vận hành Benchmark thực nghiệm đa kiến trúc (CP5):**
   - Thiết lập và thực thi ma trận benchmark toàn diện trên cả 4 hình thái kiến trúc (Workflow, Single ReAct, Orchestrator, Swarm) qua 5 seed công khai (`11, 22, 33, 44, 55`) trên 14 claims public (tổng cộng 280 trials).
   - Thu thập và phân tích định lượng 5 trục chỉ số cốt lõi: Tỉ lệ đạt (`pass_rate`), Tỉ lệ đạt toàn diện 5 seed (`pass^5`), Phương sai giữa các seed (`seed_variance`), Chi phí token/tool cho mỗi lần thành công (`cost_per_success`), và Số bước thực thi (`steps`).
4. **Xây dựng hồ sơ Kiến trúc và Báo cáo khoa học:**
   - Soạn thảo hồ sơ quyết định kiến trúc [report/team/decision_adr.md](file:///d:/LAB08/K5-L3A-DAY08-SCP404-FromWorkflowsToAgents/report/team/decision_adr.md), lập luận chặt chẽ bảo vệ việc lựa chọn **Shape A (Workflow)** cho bài kiểm tra ẩn (hidden test) dựa trên nguyên lý *"chọn kiến trúc ít tự chủ nhất mà vẫn hoàn thành tốt công việc"*.
   - Soạn thảo phiếu nghiên cứu [report/team/research_card.md](file:///d:/LAB08/K5-L3A-DAY08-SCP404-FromWorkflowsToAgents/report/team/research_card.md) nối tiếp chủ đề **R2 (Failure Taxonomy)** theo bài báo MAST (NeurIPS 2025).
5. **Kiểm định nghiệm thu tự động (Final Gate):**
   - Vận hành công cụ `lab8.check_submission`, phối hợp rà soát lỗi format, rà soát rò rỉ secret/PII và đồng bộ cây lịch sử Git để đảm bảo đạt chuẩn **0 FAIL, 0 WARN**.

---

## 3. Đóng góp cụ thể

### A. Phân tích nguyên nhân thất bại của Swarm tại Seed 55
Qua phân tích chi tiết mã nguồn `swarm_reference.py` (dòng 60–65):
```python
ticket = claim_row["ticket"]
complete(budget, seed=seed, purpose="peer", prompt=ticket)
parsed_delay = parse_delay_days(ticket)
complete(budget, seed=seed, purpose="parse", prompt=ticket)
```
Khi `seed % 5 == 0` (cụ thể là seed 55), mô hình MockLLM trong Swarm được cài đặt để kích hoạt hành vi mô phỏng: *Mô hình bị dẫn dắt bởi thông tin cảm tính của người dùng trong ticket thay vì dữ liệu thật trong cơ sở dữ liệu*.
- Cụ thể tại claim `C-002`: Khách hàng khai báo trong ticket là kiện hàng bị trễ 5 ngày (đòi bồi hoàn), nhưng dòng `orders` trong database xác nhận hàng chỉ giao trễ 2 ngày (chưa đủ ngưỡng $\ge$ 3 ngày theo quy định).
- Swarm ở seed 55 đã trích xuất `parsed_delay = 5` và tự đề xuất bồi thường 30.000 VNĐ (`status = resolved`), trong khi kết quả đúng nghiệp vụ phải là từ chối (`status = denied`). 
- **Kết luận kỹ thuật:** Đây là minh chứng thực nghiệm điển hình cho lỗi *Lệch mục tiêu / Tin vào dữ liệu không kiểm chứng* (Goal Drift / Unverified Context Injection) trong hệ thống Multi-Agent, dẫn đến phương sai dao động lớn giữa các seed.

### B. Xây dựng Unit Test cá nhân độc lập (`src/tests/test_manh_eval.py`)
Để đóng góp vào hệ thống kiểm thử tự động của nhóm và đáp ứng tiêu chí C8, tôi đã tự thiết kế và cài đặt file test `src/tests/test_manh_eval.py` gồm 2 hàm kiểm thử:
1. `test_swarm_determinism_same_seed`: Kiểm tra tính xác định (determinism). Khi cố định `seed = 11` trên cùng claim `C-001`, hệ thống chạy 2 lần độc lập phải cho kết quả hoàn toàn trùng khớp: `proposal_amount == 35000` và `status == "resolved"`.
2. `test_swarm_variance_on_seed_55`: Cô lập và kiểm chứng hiện tượng phương sai seed trên `C-002`. Khởi tạo database tạm độc lập (`tmp_path`), chứng minh kết quả trial_pass với seed 11 trả về `True` (chính xác), nhưng seed 55 trả về `False` (thất bại do tin ticket).

### C. Vận hành Crash Suite và Giám sát tính Bền vững
- Trực tiếp thực thi công cụ kiểm thử sự cố:
  ```powershell
  python -m lab8.crash_test --count 20 --out reports/crash.json
  ```
- Phân tích 20 kịch bản crash xác định:
  - Điểm 1–5: Crash tại thời điểm `before_effect` (trước khi ghi ledger) $\rightarrow$ kiểm tra việc resume không để lại effect rác.
  - Điểm 6–12: Crash tại `after_effect_before_checkpoint` (đã ghi effect nhưng chưa ghi checkpoint) $\rightarrow$ điểm kiểm tra sống còn: host phải nhận diện được effect đã commit qua idempotency key `refund:{claim_id}`, không được ghi thêm effect thứ hai.
  - Điểm 13–17: Crash tại `after_checkpoint` $\rightarrow$ khôi phục trạng thái chuẩn xác.
  - Điểm 18: `idempotent_reissue` (gọi lại cùng claim nhiều lần không tăng số dòng ledger).
  - Điểm 19: `retry_without_approval` (gọi lại khi approval đã bị revoke thì không được ghi refund mới).
  - Điểm 20: `swarm_crash` (kiểm tra khả năng chịu lỗi tích hợp trên Swarm).
- **Kết quả:** Đạt điểm tuyệt đối **`crash_safety = 20/20`**, được lưu trữ nguyên vẹn tại [src/reports/crash.json](file:///d:/LAB08/K5-L3A-DAY08-SCP404-FromWorkflowsToAgents/src/reports/crash.json).

### D. Đo lường Benchmark và Quyết định Kiến trúc (ADR)
- Thực thi benchmark trên 4 hình thái kiến trúc và 5 seed (`11, 22, 33, 44, 55`):
  ```powershell
  python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
  ```
- Phân tích kết quả thực nghiệm để đưa ra quyết định kiến trúc:
  - Shape A (Workflow) vượt trội hoàn toàn: đạt `pass_rate = 1.0`, `pass^5 = 1.0`, `variance = 0.000000`, với chi phí chỉ **28.80 VNĐ/success** (tiết kiệm hơn 39% so với Single ReAct, 39.2% so với Orchestrator, và 41.9% so với Swarm).
  - Lập luận bảo vệ trong ADR: Bản chất bài toán hoàn phí LogiX-VN là bài toán quy tắc xác định (deterministic rules: thời gian trễ, chính sách hiệu lực, trần theo đơn). Việc trao quyền tự chủ cho LLM hoặc phân tán thành Multi-Agent chỉ làm tăng chi phí token, độ trễ và rủi ro phương sai (như Swarm bị lỗi ở seed 55). Do đó, Shape A là lựa chọn tối ưu nhất.

---

## 4. Bằng chứng thực nghiệm

### A. Lịch sử Commit cá nhân trên Git
- `aba170e`: `feat(eval): finalize CP4 and CP5 deliverables by Tran Duc Manh` (chạy benchmark, tạo crash.json, viết test_manh_eval.py).
- `3f9126a`: `docs: finalize team reports and decision record` (hoàn thiện hồ sơ ADR và phiếu nghiên cứu).
- `4327e1d`: `merge: sync reports from team members and update MSSV 2A202603615` (đồng bộ báo cáo nhóm và mã số sinh viên chính thức).

### B. Bảng số liệu Benchmark tổng hợp (Trích xuất từ `src/reports/benchmark.json`)

| Kiến trúc | Số Trials | Pass Rate | Pass^5 | Min Seed | Max Seed | Seed Variance | Cost / Success (VNĐ) | Mean Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Shape A (Workflow)** | **70** | **1.000** | **1.000** | **1.000** | **1.000** | **0.000000** | **28.80** | **4.43** |
| **Shape B (Single Agent)** | 70 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000000 | 47.22 | 8.64 |
| **Shape C (Orchestrator)** | 70 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000000 | 47.37 | 5.36 |
| **Shape D (Swarm Ref)** | 70 | 0.986 | 0.929 | 0.929 | 1.000 | 0.000816 | 49.57 | 2.80 |

### C. Kết quả kiểm thử tự động
1. Bài kiểm thử cá nhân:
   ```powershell
   python -m pytest -q tests/test_manh_eval.py
   # Kết quả: 2 passed in 0.38s
   ```
2. Bộ kiểm thử Crash Suite:
   ```powershell
   python -m lab8.crash_test --count 20 --out reports/crash.json
   # Kết quả: crash_safety 20/20 (20 passed)
   ```
3. Kiểm thử nghiệm thu tổng thể:
   ```powershell
   python -m lab8.check_submission
   # Kết quả: 0 FAIL, 0 WARN (commit hash: 4327e1d)
   ```

### D. Run ID dẫn chứng
- Run ID dẫn chứng hiệu năng Workflow: `R-workflow-C-001-s11` (Status: `resolved`, Amount: 35.000 VNĐ, Cost: 28.80 VNĐ).
- Run ID dẫn chứng lỗi phương sai Swarm: `R-swarm-C-002-s55` (Status: `resolved` $\ne$ Expected: `denied` do tin vào số ngày trễ 5 ngày trong ticket).

---

## 5. Công cụ AI đã dùng

Tuân thủ nghiêm ngặt quy định liêm chính học thuật trong [RULES.md](file:///d:/LAB08/K5-L3A-DAY08-SCP404-FromWorkflowsToAgents/RULES.md):

- **Công cụ sử dụng:** Antigravity Assistant (Google DeepMind).
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích luật nghiệp vụ trong `docs/business_rules.md` và cấu trúc Trace contract v1 trong `docs/contracts.md`.
  - Tham vấn cú pháp thiết kế fixture kiểm thử độc lập cho Pytest (`tmp_path`, `public_db`).
  - Hỗ trợ định dạng và rà soát lỗi cú pháp trong các file Markdown chuẩn bị nộp (`decision_adr.md`, `research_card.md`).
- **Phương pháp tự kiểm chứng độc lập:**
  - Tuyệt đối không để AI tự ý sửa đổi các file thước đo cấm (`metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`).
  - Mọi số liệu trong báo cáo đều được trích xuất trực tiếp bằng câu lệnh thực tế từ các file do script sinh ra (`src/reports/benchmark.json`, `src/reports/crash.json`), không chỉnh sửa thủ công bất kỳ số liệu nào.
  - Toàn bộ các bài test và lệnh nghiệm thu đều được chạy lại độc lập trong terminal máy cá nhân trước khi thực hiện commit và push lên GitHub.

---

## 6. Tự đánh giá

### Ưu điểm đạt được:
- Hoàn thành trọn vẹn và đúng hạn toàn bộ trách nhiệm cá nhân theo phân công trong nhóm, đóng vai trò then chốt trong việc đo lường, nghiệm thu và ra quyết định kiến trúc ở CP4 và CP5.
- Đảm bảo 3 điều kiện **Must-Pass** sống còn của bài Lab: Crash safety đạt 20/20 tuyệt đối, không rò rỉ secret/PII trong trace, và không bao giờ phê duyệt trái phép khi thiếu approval hợp lệ.
- Xây dựng được bài unit test độc lập có giá trị thực nghiệm cao, giúp nhóm chứng minh rõ hiện tượng phương sai seed của Swarm.
- Đưa ra quyết định kiến trúc dựa trên cơ sở khoa học và dữ liệu định lượng cụ thể, không bị chi phối bởi định kiến "Multi-Agent luôn tốt hơn".

### Giới hạn và Hướng mở rộng:
- Môi trường thực nghiệm dựa trên mô hình giả lập `MockLLM` với bảng giá token quy đổi cố định; các chỉ số đo độ trễ (latency) ghi nhận `unavailable`.
- Trong môi trường sản xuất thực tế với các LLM quy mô lớn (như Gemini 1.5 Pro hay GPT-4o), chi phí thực tế và độ trễ mạng có thể làm khoảng cách giữa Workflow và Multi-Agent mở rộng hơn nữa. Nếu bài toán trong tương lai yêu cầu phân tích phi cấu trúc (như phân tích hình ảnh hư hỏng hàng hóa hoặc OCR hóa đơn), kiến trúc có thể cần chuyển dịch sang Single Agent có chốt chặn kiểm soát (Guardrails) nghiêm ngặt từ Host.
