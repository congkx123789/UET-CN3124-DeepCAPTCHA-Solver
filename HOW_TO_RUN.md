# Hướng dẫn chạy và cấu trúc dự án CTF Auto Solver

Dự án này là hệ thống giải mã tự động CAPTCHA để vượt qua cơ chế phòng thủ của hệ thống mục tiêu phục vụ cho bài tập lớn môn **UET.CN3124**.

---

## 1. Cấu trúc thư mục dự án

```text
CTF_Auto_Solver/
├── server/                   # Thư mục chứa Target Server (FastAPI)
│   ├── main.py               # API chính phục vụ ảnh CAPTCHA và kiểm tra flag
│   ├── captcha_gen.py        # Thư viện và công cụ sinh CAPTCHA tự động
│   ├── Dockerfile            # Cấu hình container hóa ứng dụng server
│   └── templates/            # Giao diện web giao tiếp với server
│
├── ai_model/                 # Thư mục huấn luyện mô hình AI học máy
│   ├── model.py              # Định nghĩa kiến trúc mạng CRNN (CNN + GRU + CTC Loss)
│   ├── dataset.py            # Quản lý, tải và tiền xử lý ảnh đầu vào
│   ├── train.py              # Mã nguồn huấn luyện mô hình CRNN
│   ├── evaluate.py           # Đánh giá độ chính xác mô hình trên tập kiểm thử
│   └── weights/              # Nơi lưu trữ trọng số mô hình đã huấn luyện
│       └── best_model.pth    # Trọng số tốt nhất đạt độ chính xác cao (~85%)
│
├── solver/                   # Thư mục mã nguồn tấn công/giải tự động
│   ├── exploit.py            # Kịch bản gửi request liên tục lấy CAPTCHA và giải
│   └── utils.py              # Các tiện ích hỗ trợ dự đoán và tiền xử lý ảnh
│
├── dataset/                  # Tập dữ liệu sinh ra cục bộ để huấn luyện (được gitignore)
├── docker-compose.yml        # Cấu hình khởi chạy nhanh server qua Docker Compose
├── requirements.txt          # Các thư viện Python cần thiết cho AI và Solver
├── run_attack.sh             # Kịch bản Bash chạy thử nghiệm nhanh toàn bộ luồng
└── logbook.md                # Nhật ký quá trình phát triển hệ thống
```

---

## 2. Cách thiết lập môi trường và chạy dự án

Bạn có hai cách để khởi chạy dự án: **Chạy nhanh bằng Script Bash (Khuyên dùng)** hoặc **Chạy thủ công từng bước**.

### Cách 1: Chạy nhanh bằng Script Tự động (`run_attack.sh`)

Script này sẽ tự động khởi chạy FastAPI Server ở chế độ nền (background), đợi server khởi động, sau đó thực thi file giải mã `solver/exploit.py` để thực hiện bypass 50 lần liên tiếp lấy flag và cuối cùng tự động tắt server khi chạy xong.

Để chạy:
```bash
# Cấu hình cấp quyền thực thi cho script
chmod +x run_attack.sh

# Chạy script
./run_attack.sh
```

---

### Cách 2: Chạy thủ công từng bước

#### Bước 1: Khởi tạo môi trường ảo (Virtual Environment)
Để đảm bảo môi trường sạch sẽ và không bị xung đột thư viện:
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
source venv/bin/activate

# Cài đặt thư viện cần thiết
pip install -r requirements.txt
```

#### Bước 2: Chạy Target Server
Bạn có thể khởi động server trực tiếp hoặc qua Docker.

* **Chạy trực tiếp bằng Python:**
  ```bash
  python server/main.py
  ```
  *(Server sẽ chạy tại địa chỉ http://localhost:8000)*

* **Chạy bằng Docker (Nếu muốn môi trường độc lập hoàn toàn):**
  ```bash
  docker-compose up -d --build
  ```

#### Bước 3: Chạy kịch bản giải CAPTCHA tự động (`solver`)
Khi server đã hoạt động, chạy script exploit để thực hiện tấn công giải mã 50 CAPTCHA liên tục nhằm lấy flag:
```bash
python solver/exploit.py
```

---

## 3. Huấn luyện lại mô hình AI (Nếu cần)

Trong trường hợp bạn muốn tạo thêm dữ liệu hoặc huấn luyện lại mô hình từ đầu:

1. **Sinh dữ liệu ảnh CAPTCHA mới:**
   ```bash
   python server/captcha_gen.py --count 20000
   ```
   *(Ảnh sinh ra sẽ nằm trong thư mục `dataset/`)*

2. **Tiến hành huấn luyện mô hình:**
   ```bash
   python ai_model/train.py
   ```
   *(Sau khi huấn luyện xong, mô hình có độ chính xác tốt nhất sẽ tự động được lưu đè vào `ai_model/weights/best_model.pth`)*

3. **Kiểm tra độ chính xác của mô hình:**
   ```bash
   python ai_model/evaluate.py
   ```
