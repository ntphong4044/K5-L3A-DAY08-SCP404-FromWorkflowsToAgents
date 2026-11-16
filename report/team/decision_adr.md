# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: aba170e
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 28.80
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng tập kiểm thử public (14 claim x 5 seed = 70 trial), Shape A (Workflow) đạt tỷ lệ thành công tuyệt đối 100% (pass_rate = 1.0, pass^5 = 1.0) với độ dao động bằng 0 (variance = 0.000000) và chi phí thấp nhất trong cả 4 kiến trúc (28.80 VND/success, so với 47.22 VND của Single, 47.37 VND của Orchestrator và 49.57 VND của Swarm). 
Quy trình xử lý claim hoàn phí của LogiX-VN có luồng nghiệp vụ rõ ràng, logic tính tiền và kiểm tra điều kiện đều là deterministic code (`compute_compensation`, trần theo đơn, approval binding). Việc đưa LLM vào tự chủ ra quyết định hay gọi nhiều agent không mang lại giá trị gia tăng về độ chính xác mà chỉ làm tăng chi phí token, latency và rủi ro phương sai (như Swarm bị fail ở seed 55 do tin vào ticket người dùng). Theo nguyên lý "chọn kiến trúc ít tự chủ nhất mà vẫn hoàn thành tốt công việc", Workflow là lựa chọn tối ưu và vững chắc nhất.

## Có đáng đổi lấy multi-agent không

Hoàn toàn không đáng đổi trong bài toán này. Swarm và Orchestrator có chi phí trên mỗi lần thành công cao hơn từ 64% đến 72% so với Workflow, đồng thời Swarm xuất hiện phương sai thất bại (pass rate giảm xuống 0.986, pass^5 giảm xuống 0.929 ở seed 55).
Quyết định chỉ có thể đảo lại (đổi sang multi-agent) khi và chỉ khi:
1. Đề bài có yêu cầu phân tích phi cấu trúc phức tạp vượt quá khả năng của rule-based code (ví dụ: cần đọc hiểu hình ảnh kiện hàng hư hỏng đa góc độ, trích xuất hóa đơn scan OCR đa ngôn ngữ, hoặc đối chiếu đàm phán hợp đồng logistics phức tạp).
2. Tác vụ có thể phân rã thành các miền nghiệp vụ độc lập cần điều tra song song với các công cụ chuyên biệt có quyền hạn khác nhau mà một luồng tuần tự không thể đảm đương hiệu quả.

## Trace và bằng chứng

Trace của Workflow ghi lại tối giản và có chủ đích các sự kiện theo đúng Trace contract v1:
- `start`: Khởi tạo phiên xử lý với `claim_id`, `seed`.
- `decision`: Ghi nhận quyết định trạng thái (`needs_info`, `escalated`, `denied`, `resolved`) cùng `proposal_amount`.
- `effect`: Ghi nhận kết quả gọi cổng host `durability.issue_refund` khi quote > 0.
- `finish`: Hoàn tất phiên và ghi nhận kết quả cuối.

**Field cố ý KHÔNG ghi:**
- Không bao giờ ghi dòng claim thô (`claim_row`) hay dòng order thô (`order_row`).
- Tuyệt đối loại bỏ các trường PII (số điện thoại, địa chỉ giao hàng, tên mặt hàng, ghi chú nội bộ `internal_note`) và các chuỗi bí mật `CANARY_SECRET_*`.
- Để chứng minh hệ thống không lộ secret ngay cả khi trace nằm ngoài phạm vi scanner: Đội security có thể kiểm tra qua kiến trúc phân quyền (Least Privilege) - Host là chốt chặn duy nhất kiểm soát ghi dữ liệu, các hàm đọc qua view đã được lọc schema (`get_claim_view`), và kết quả trả về `RunResult` chỉ chứa các metadata đã được sanitize trong hợp đồng.

## Giới hạn

MockLLM không phải model sản xuất thực tế (các bẫy seed được mô phỏng có chủ đích). Latency của hệ thống để `unavailable` do chạy giả lập nội bộ. Toàn bộ số liệu được trích xuất trung thực từ file `src/reports/benchmark.json` và `src/reports/crash.json`, không có bất kỳ sự chỉnh sửa thủ công nào.
