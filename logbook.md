# NHẬT KÝ LÀM VIỆC (LOGBOOK)
**Đồ án thực hành CTF Jeopardy - Học phần UET.CN3124**
**Sinh viên thực hiện:** 23020014
**Tổng thời gian thực hiện dự kiến:** ~30 giờ làm việc cá nhân

---

## TUẦN 1: TÌM HIỂU BÀI TOÁN VÀ THIẾT LẬP MÔI TRƯỜNG CƠ BẢN
### Ngày 1 (4 giờ) - Khảo sát Server & Phân tích cơ chế CAPTCHA
- **Mục tiêu:** Phân tích giao thức giao tiếp HTTP và độ khó của ảnh CAPTCHA sinh ra từ Server.
- **Giả thuyết kỹ thuật:** Server cấp phát ảnh ngẫu nhiên từ 4-7 ký tự, bị xoay góc (-20 đến 20 độ) và thêm đường kẻ nhiễu Bezier. Các công cụ OCR tĩnh (Tesseract) sẽ không thể cắt (segmentation) từng ký tự do chữ bị dính liền.
- **Thử nghiệm lệnh:**
  ```bash
  curl -s http://localhost:8000/challenge | jq .
  ```
- **Kết quả & Nhận xét:** Nhận về chuỗi Base64. Thử nghiệm Tesseract OCR cho kết quả chính xác 0%. Chốt phương án sử dụng Mạng học sâu không cần phân mảnh: **CRNN + CTC Loss**.

### Ngày 2 (4 giờ) - Xây dựng kịch bản giả lập & Sinh tập dữ liệu (Dataset Generator)
- **Mục tiêu:** Viết script `generate_dataset.py` giả lập chính xác thuật toán sinh CAPTCHA của máy chủ đích.
- **Lệnh thực thi:**
  ```bash
  python server/captcha_gen.py --count 20000
  ```
- **Lỗi gặp phải:** Tốc độ sinh ảnh bằng thư viện `captcha.image` quá chậm khi sinh 20,000 ảnh.
- **Khắc phục:** Tối ưu hóa I/O, lưu tên file theo nhãn (VD: `AB3K_1234.png`) để DataLoader đọc trực tiếp từ tên file mà không cần ghi file CSV lập chỉ mục.

---

## TUẦN 2: THIẾT KẾ VÀ HUẤN LUYỆN MẠNG NEURAL (CRNN)
### Ngày 3 (6 giờ) - Xây dựng kiến trúc mô hình (Model Architecture)
- **Mục tiêu:** Implement kiến trúc CRNN bằng PyTorch tại `ai_model/model.py`.
- **Giả thuyết kỹ thuật:** 7 lớp Conv2d kết hợp BatchNorm và MaxPool kích thước đặc biệt (4, 1) ở cuối sẽ ép chiều cao ma trận đặc trưng về 1 mà vẫn bảo toàn chuỗi thời gian cho Bi-LSTM.
- **Thực thi:** Khởi tạo Bi-LSTM với Hidden Size 512 units.
- **Lỗi gặp phải (OOM - Tràn bộ nhớ):**
  ```text
  RuntimeError: CUDA out of memory.
  ```
- **Khắc phục:** Giảm `BATCH_SIZE` từ 256 xuống 64 trong tệp `train.py`.

### Ngày 4 (6 giờ) - Huấn luyện mô hình (Warm-up & Fine-tuning)
- **Mục tiêu:** Chạy tiến trình huấn luyện trên tập 20,000 ảnh Train và 10,500 ảnh Val.
- **Lệnh thực thi:**
  ```bash
  python ai_model/train.py
  ```
- **Lỗi gặp phải (Underfitting & Plateau):** Mô hình chững lại (Plateau) ở độ chính xác 78% tại Epoch 6, không thể tăng tiếp.
- **Khắc phục:** Dừng tiến trình, tinh chỉnh (Fine-tuning) giảm Learning Rate từ `1e-3` xuống `1e-4` và thêm phép xoay dữ liệu `RandomRotation(20)`. Tiếp tục Resume từ Checkpoint.
- **Kết quả thu được:** Độ chính xác vọt lên **84.93%** tại tệp `best_model.pth`. Đã sẵn sàng cho thực chiến.

---

## TUẦN 3: TỰ ĐỘNG HÓA KHAI THÁC & HOÀN THIỆN HỆ THỐNG
### Ngày 5 (6 giờ) - Viết mã khai thác tự động (Exploit Loop)
- **Mục tiêu:** Viết tệp `solver/exploit.py` thực thi vòng lặp 50 HTTP Request liên tiếp trong thời gian quy định.
- **Giả thuyết kỹ thuật:** Để đạt Streak 50 liên tiếp với độ chính xác model 85%, hệ thống cần xử lý tự động với tốc độ cực nhanh (tránh hết hạn Session).
- **Thực thi:** Xử lý ảnh trực tiếp trên RAM bằng `PIL.Image.open(BytesIO())`.
- **Lệnh thực thi:**
  ```bash
  python solver/exploit.py
  ```
- **Kết quả:** Hệ thống đạt hiệu suất 10-15 ảnh/giây, lưu lại các ảnh giải sai vào thư mục `failed_captchas` để tiếp tục mổ xẻ. Thành công đoạt cờ `FLAG{...}` sau các lượt thử nghiệm.

### Ngày 6 (4 giờ) - Tối ưu hóa môi trường & Viết báo cáo tổng kết
- **Mục tiêu:** Tách biệt "Môi trường sạch" (Clean Environment) theo chuẩn an toàn thông tin và hoàn thiện báo cáo.
- **Thực thi:**
  - Viết `Dockerfile` và `docker-compose.yml` để đóng gói hoàn toàn Target Server.
  - Sử dụng Virtual Environment (`venv`) cho không gian tấn công.
  - Tích hợp module `logging` ghi log tự động vào thư mục `logs/`.
  - Chạy `build_pdf.py` và kiểm tra chất lượng tệp nộp.
