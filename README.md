# Chatbot Tuyển Sinh Thạc Sĩ UIT

Chatbot hỗ trợ tư vấn tuyển sinh thạc sĩ Trường Đại học CNTT (UIT) – Đại học Quốc gia TP.HCM. Hệ thống sử dụng Rasa và giao diện web thân thiện, có thể chạy hoàn toàn trên máy cá nhân.

## 1. Yêu cầu hệ thống

- Python 3.8+
- Node.js & npm (để cài đặt LocalTunnel nếu muốn chia sẻ qua internet)
- pip, venv (quản lý môi trường ảo)

## 2. Cài đặt

### Bước 1: Clone và tạo môi trường ảo

```bash
git clone <repo-url>
cd chatbot
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 2: Cài đặt các thư viện Python

```bash
pip install -r requirements.txt
```

### Bước 3: Train mô hình Rasa

```bash
rasa train
```

## 3. Chạy chatbot và giao diện web trên local

### Bước 1: Khởi động Rasa Action Server

```bash
rasa run actions --cors "*"
```

### Bước 2: Khởi động Rasa Server

Mở terminal mới (vẫn trong môi trường ảo):

```bash
rasa run --enable-api --cors "*"
```

### Bước 3: Khởi động UI Server

Mở terminal mới (vẫn trong môi trường ảo):

```bash
python serve_ui.py
```

### Bước 4: Truy cập giao diện web

Mở trình duyệt và truy cập:  
```
http://localhost:8000?server=http://localhost:5055
```
- Giao diện web sẽ kết nối trực tiếp với Rasa server local.
- Bạn có thể chat và kiểm tra các chức năng chatbot.

## 4. Cấu trúc thư mục chính

```
chatbot/
├── actions.py           # Custom actions cho Rasa
├── config.yml           # Cấu hình pipeline Rasa
├── credentials.yml      # Cấu hình kênh giao tiếp (REST)
├── data/                # Dữ liệu NLU, stories, rules
├── domain.yml           # Định nghĩa intent, entity, slot, response
├── endpoints.yml        # Cấu hình endpoint cho action server
├── logs/                # Log server và UI
├── models/              # Mô hình đã train
├── requirements.txt     # Thư viện Python cần thiết
├── serve_ui.py          # Server Python phục vụ giao diện web
├── static/              # Thư mục chứa UI: index.html, script.js, style.css
└── run_with_localtunnel.sh # Script chạy tự động (nếu muốn chia sẻ qua internet)
```

## 5. Một số lưu ý

- Đảm bảo cả 3 server (action, rasa, ui) đều đang chạy trước khi truy cập giao diện web.
- Nếu muốn chia sẻ chatbot qua internet, sử dụng script `run_with_localtunnel.sh` (xem hướng dẫn trong script).
- Nếu gặp lỗi CORS, đảm bảo bạn đã bật `--cors "*"` khi chạy các server.
- Để dừng server, chỉ cần nhấn `Ctrl+C` tại terminal tương ứng.

---

Nếu cần bổ sung thông tin hoặc hướng dẫn chi tiết cho deploy qua LocalTunnel, hãy cho tôi biết!
