# Bonus report: B3

- Topic + nguồn (tên, năm, slide): B3 · Verifier/aggregator chống khuếch đại lỗi. Google Research 2026, *Towards a Science of Scaling Agent Systems* (error amplification). Slide 17 (Evaluator–optimizer), 22 (Reflection), 42.
- CLAIM của nguồn (1 câu): agent độc lập khuếch đại lỗi tới 17,2×, còn orchestration tập trung có bước kiểm tra giảm xuống 4,4×.
- BOUNDARY (model / dataset / setup): đo trên LLM thật, nhiều benchmark agentic, đếm lỗi lan truyền giữa nhiều agent. Ở LogiX chỉ có một nguồn lỗi cố định do MockLLM cài sẵn (swarm tin số ngày trễ trong ticket khi `seed % 5 == 0`), không có lỗi ngẫu nhiên hay lan truyền nhiều tầng.
- HYPOTHESIS trên LogiX: thêm một verifier bằng code đối chiếu dữ kiện quote với order row sẽ đưa swarm về pass rate và variance bằng workflow (1.0 / 0.0), chi phí tăng không quá 1 tool call cho mỗi lần can thiệp; cost/success vẫn cao hơn workflow khoảng 1,7× vì peer và parse model calls vẫn còn.
- Biến cố định / biến thay đổi: cố định MockLLM, tool, bảng giá, seed `11,22,33,44,55`, evaluator `lab8.metrics.trial_pass`, corpus. Biến thay đổi duy nhất: có hay không bước verifier (`swarm` so với `swarm_verified`); `workflow` là mốc so sánh.
- Lệnh tái lập (copy-paste được, chạy trong `src/`):
  - `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json`
  - `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_benchmark_adversarial.json`
  - `python -m bonus.verifier_stats --out reports/bonus_b3_summary.json`
  - `python -m pytest -q tests/test_bonus_swarm_verified.py`
- File report + run id: `src/reports/bonus_benchmark_public.json`, `src/reports/bonus_benchmark_adversarial.json`, `src/reports/bonus_b3_summary.json`. Run id minh họa: `R-swarm-C-002-s55` (swarm sai) và `R-swarm_verified-C-002-s55`, `R-swarm_verified-B-01-s55` (verifier sửa).

## Kết quả

**Thiết kế.** `bonus/swarm_verified.py` giữ nguyên swarm (peer, parse, investigator chỉ đọc, và cả điểm yếu tin ticket ở seed % 5 == 0). Chỉ thêm một bước sau khi swarm đã có quote và trước mọi quyết định: so `delay_days`, `status`, `damage_verified` mà quote đã dùng với order row của investigator. Lệch thì quote lại từ order row, tối đa 1 vòng, và ghi `verifier_override` (chỉ tên field) vào trace. Verifier là code, không phải model.

**Bộ claim đối kháng tự viết** (`bonus/cases.jsonl`, `bonus/world.json`, 10 claim, nhãn viết tay theo `docs/business_rules.md`): nói quá (B-01, B-07 sát ngưỡng 3 vs 2), nói thiếu (B-02 ticket 1 ngày / DB 5), nói dối hỏng hàng (B-03), nhiều con số trong câu (B-04), nói quá trên đơn `cancelled` (B-05), đòi cộng hai khoản (B-06), injection kèm nói quá (B-08), đối chứng không dấu (B-09), nói thiếu trên đơn đã hoàn đủ (B-10). Kiểm chéo nhãn: workflow (không đọc ticket) đạt 50/50 trên bộ này.

Số liệu từ `reports/bonus_b3_summary.json` (5 seed):

| Corpus | Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND) | Refund sai nhãn | Leak |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| Public (14 claim) | workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.80 | 0 | 0 |
| | swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 1 | 0 |
| | swarm_verified | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 49.00 | 0 | 0 |
| Đối kháng (10 claim) | workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 30.94 | 0 | 0 |
| | swarm | 0.900 | 0.500 | 0.500–1.000 | 0.040000 | 60.01 | 3 | 0 |
| | swarm_verified | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 55.61 | 0 | 0 |

"Refund sai nhãn" = trial `resolved` trong khi nhãn không có refund. Approval vẫn hợp lệ ở các claim này, nên host không chặn được: đây là tiền chi sai mà chỉ verifier phía shape ngăn được.

**Số lần verifier can thiệp:** public 1/70 trial, đối kháng 8/50 trial, tất cả ở seed 55 (đúng điểm yếu cài sẵn). Trong 8 lần ở bộ đối kháng, 5 lần đổi kết quả từ sai thành đúng (B-01, B-02, B-07, B-08, B-10) và 3 lần can thiệp nhưng kết quả đã đúng sẵn (B-04, B-05, B-06: quote không đổi vì số ngày trễ không phải yếu tố quyết định). Swarm fail đúng 5 claim trên, tất cả ở seed 55.

**Chi phí của verifier:** tổng chi phí mô phỏng trên bộ đối kháng 2700.32 → 2780.30 VND (+80, tức 8 tool call × 10 VND), trên public 3420.12 → 3430.10 (+10). Cost/success của swarm_verified *thấp hơn* swarm (55.61 so với 60.01) vì số lần thành công tăng 45 → 50 nhiều hơn mức tăng chi phí. Nhưng vẫn cao hơn workflow 1,7–1,8× vì 3 model call mỗi claim (peer, parse, draft) so với 1 của workflow.

**Trace minh họa** (`traces/R-swarm_verified-B-01-s55.json`, ticket nói 7 ngày, DB 1 ngày): `handoff` → `investigator` (order view allowlist, `delay_days: 1`) → `model_override {delay_days: 7}` → `verifier_override {fields: ["delay_days"], requoted_from: "order_row"}` → `quote {amount_vnd: 0, reason: no_entitlement}` → `denied`.

## Kết luận

**Ủng hộ hypothesis trên LogiX.** Verifier đưa swarm về đúng mức của workflow: pass rate 1.0, pass^5 1.0, variance 0 trên cả hai corpus, không còn refund sai nhãn; chi phí thêm đúng 1 tool call cho mỗi lần can thiệp. Kết quả cùng chiều với claim của nguồn (một bước kiểm tra tập trung chặn lỗi trước khi nó thành hành động), nhưng không đo được hệ số khuếch đại vì LogiX chỉ có một agent gây lỗi và một tầng.

**Swarm còn giữ giá trị gì?** Trên task này gần như không. Verifier thay toàn bộ phần quyết định bằng dữ liệu có cấu trúc, nên mọi thứ peer và parse đọc từ ticket đều bị bỏ qua khi đến lúc tính tiền. Swarm_verified chỉ là workflow đắt hơn 1,7–1,8×. Điều này ủng hộ quyết định trong ADR: chọn kiến trúc ít tự chủ nhất mà vẫn làm được việc.

**Điều kiện đảo ngược:**
- Nếu dữ kiện quyết định *không có* trong DB (ví dụ mô tả hư hỏng chỉ có trong ảnh hoặc chữ của khách, chưa ai verify), verifier bằng code không có gì để đối chiếu; khi đó phần đọc ticket của agent mới có giá trị và cần verifier khác (con người hoặc nguồn thứ hai).
- Nếu order row sai (dữ liệu bẩn) mà ticket đúng, verifier sẽ ép kết quả theo dữ liệu sai; claim B-02 cho thấy hướng ngược lại vẫn đúng chỉ vì nhãn tin DB.
- Nếu lỗi của model nằm ở field verifier không kiểm (ví dụ `shipping_fee_vnd`, `paid_vnd`), cần mở rộng `VERIFIED_FIELDS`.

## Giới hạn

- MockLLM không phải model sản xuất: lỗi là deterministic, chỉ ở seed % 5 == 0 và chỉ ở `delay_days`. Với LLM thật, lỗi có thể ở field khác hoặc ở cách hiểu policy, và verifier có thể bỏ sót.
- Chi phí là VND mô phỏng theo `config/pricing.yaml`, latency `unavailable`.
- Bộ đối kháng nhỏ (10 claim, 1 principal), nhãn do nhóm viết tay; workflow đạt 50/50 trên bộ này chỉ cho thấy nhãn nhất quán với luật nghiệp vụ, không chứng minh nhãn đầy đủ.
- 5 seed, trong đó chỉ seed 55 kích hoạt lỗi, nên variance của swarm phụ thuộc hoàn toàn vào một seed.
