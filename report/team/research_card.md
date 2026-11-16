# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, https://arxiv.org/abs/2503.xxxxx, benchmark phân loại nguyên nhân thất bại trong hệ thống Multi-Agent |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống Multi-Agent gặp rủi ro thất bại cao do sai lệch mục tiêu (goal drift) và tin vào dữ liệu ngữ cảnh không kiểm chứng khi có thông tin người dùng gây nhiễu |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Môi trường mô phỏng MockLLM với bộ 14 claim public LogiX-VN chạy trên 5 seed xác định (11, 22, 33, 44, 55) |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu chuyển từ Workflow (Shape A) sang Swarm (Shape D), variance sẽ tăng từ 0.0 lên >0 và pass rate giảm xuống dưới 1.0 (do bẫy seed 55 tin vào ticket), chi phí tăng trên 70% |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, bộ công cụ đọc, 5 seed (11, 22, 33, 44, 55), 14 claim public, bảng giá và evaluator. Biến duy nhất thay đổi: Kiến trúc điều phối (Topology: Workflow tuần tự vs Swarm cộng tác) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Thất bại ở claim C-002 tại seed 55 do tin vào số ngày trễ ghi trong ticket; đo bằng pass rate (giảm từ 1.0 xuống 0.986), pass^5 (giảm xuống 0.929), variance (tăng lên 0.000816) |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
- Run id / file report: src/reports/benchmark.json (Run id dẫn chứng lỗi: R-swarm-C-002-s55)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng hoàn toàn với giả thuyết. Swarm bị kéo tụt pass rate xuống 0.986 (70 trial pass 69, fail đúng 1 lần tại C-002 với seed 55), pass^5 đạt 0.929, variance là 0.000816, trong khi Workflow đạt 100% (pass rate 1.0, pass^5 1.0, variance 0.000000). Chi phí/success của Swarm là 49.57 VND, đắt hơn 72.1% so với Workflow (28.80 VND).
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
